import os
import uuid as _uuid
from django.utils.text import slugify
from django.db.models import Avg, Count, F, Exists, OuterRef, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import subprocess, tempfile, shutil
from .models import Category, Product, Review, ReviewPhoto, Favorite
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer,
    ProductCreateSerializer, SupplierProductSerializer,
)

from PIL import Image
from io import BytesIO


# ── Categories ────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list(request):
    # Seulement les catégories racines (parent=None) ; enfants imbriqués via get_children()
    categories = Category.objects.filter(
        parent=None, is_active=True
    ).prefetch_related('children')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# ── Public : bannière d'une catégorie pour la page de recherche ───
@api_view(['GET'])
@permission_classes([AllowAny])
def category_banner(request):
    """
    Renvoie la bannière (image + lien) de la catégorie/sous-catégorie
    correspondant au terme recherché. Match par slug (prioritaire)
    puis par nom (insensible à la casse). {'banner': None} si aucune
    catégorie ne correspond ou si elle n'a pas de bannière.
    """
    q    = (request.GET.get('q') or '').strip()
    slug = (request.GET.get('slug') or '').strip()
    if not q and not slug:
        return Response({'banner': None})

    cat = None
    if slug:
        cat = Category.objects.filter(slug__iexact=slug, is_active=True).first()
    if cat is None and q:
        cat = (Category.objects.filter(name__iexact=q, is_active=True).first()
               or Category.objects.filter(slug__iexact=slugify(q), is_active=True).first())

    if cat is None or not cat.banner_url:
        return Response({'banner': None})

    return Response({
        'banner': {
            'image_url': cat.banner_url,
            'link':      cat.banner_link or None,
        }
    })


# ── Admin : Catégories (CRUD) ─────────────────────────────────────
def _cat_dict(cat):
    return {
        'id': str(cat.id),
        'name': cat.name,
        'slug': cat.slug,
        'icon_name': cat.icon_name,
        'image_url': cat.image_url,
        'banner_url': cat.banner_url,        # ← bannière de recherche
        'banner_link': cat.banner_link,      # ← lien au clic
        'parent': str(cat.parent_id) if cat.parent_id else None,
        'parent_name': cat.parent.name if cat.parent_id else None,
        'is_hot': cat.is_hot,
        'is_new': cat.is_new,
        'is_active': cat.is_active,
        'sort_order': cat.sort_order,
        'product_count': Product.objects.filter(category=cat).count(),
    }


def _save_category(request, cat):
    is_create = cat is None
    if is_create:
        cat = Category()
    data = request.data

    if 'name' in data:
        cat.name = data.get('name', cat.name)
    if 'icon_name' in data:
        cat.icon_name = data.get('icon_name') or ''
    if 'sort_order' in data:
        try:
            cat.sort_order = int(data.get('sort_order') or 0)
        except (TypeError, ValueError):
            cat.sort_order = 0
    for flag in ('is_hot', 'is_new', 'is_active'):
        if flag in data:
            setattr(cat, flag, str(data.get(flag)).lower() in ('true', '1', 'on', 'yes'))
    if 'parent' in data:
        pval = data.get('parent')
        cat.parent = None if pval in ('', 'null', 'None', None) else Category.objects.filter(id=pval).first()

    f = request.FILES.get('image')
    if f is not None:
        ext  = os.path.splitext(f.name)[1].lower() or '.jpg'
        key  = f'categories/{_uuid.uuid4().hex}{ext}'
        path = default_storage.save(key, ContentFile(f.read()))
        url  = default_storage.url(path)
        if url.startswith('/'):
            url = request.build_absolute_uri(url)
        cat.image_url = url
    elif 'image_url' in data:
        cat.image_url = data.get('image_url') or ''

    if not (cat.name or '').strip():
        return Response({'error': 'Le nom est obligatoire.'}, status=400)

    if not cat.slug:
        base = slugify(cat.name)[:140] or 'categorie'
        slug, i = base, 2
        qs = Category.objects.filter(slug=slug)
        while (qs.exclude(id=cat.id) if cat.id else qs).exists():
            slug, i = f'{base}-{i}', i + 1
            qs = Category.objects.filter(slug=slug)
        cat.slug = slug

    cat.save()
    return Response(_cat_dict(cat), status=201 if is_create else 200)


# ── Autocomplete pro (Meilisearch + catégories + complétions) ─────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_autocomplete(request):
    q = request.query_params.get('q', '').strip()
    if len(q) < 2:
        return Response({'completions': [], 'products': [], 'categories': []})

    from . import search as meili

    # 1) Produits — Meilisearch (fuzzy), uniquement les approuvés
    try:
        res = meili.get_index().search(q, {
            'limit': 5,
            'filter': 'status = "approved"',
            'attributesToRetrieve': ['id', 'name', 'slug', 'base_price_tnd', 'primary_image'],
        })
        hits = res.get('hits', [])
    except Exception:
        hits = []

    products = [{
        'id':    h['id'],
        'name':  h['name'],
        'slug':  h.get('slug'),
        'price': h.get('base_price_tnd'),
        'image': h.get('primary_image'),
    } for h in hits]

    # 2) Catégories — depuis ta base
    cats = Category.objects.filter(
        name__icontains=q, is_active=True,
    ).values('id', 'name', 'slug')[:4]
    categories = [{'id': str(c['id']), 'name': c['name'], 'slug': c['slug']} for c in cats]

    # 3) Complétions — requêtes populaires + noms produits
    completions = _build_completions(q, hits)

    return Response({
        'completions': completions,
        'products':    products,
        'categories':  categories,
    })


def _build_completions(q, hits, limit=5):
    out, seen = [], set()
    ql = q.lower()

    # a) requêtes déjà tapées, les + fréquentes qui commencent par q
    try:
        from store.models import SearchHistory
        from django.db.models import Count
        popular = (SearchHistory.objects
                   .filter(query__istartswith=q)
                   .values('query').annotate(n=Count('id'))
                   .order_by('-n')[:limit])
        for row in popular:
            term = (row['query'] or '').strip().lower()
            if term and term not in seen:
                seen.add(term); out.append(term)
    except Exception:
        pass

    # b) complète avec des noms de produits nettoyés si pas assez
    for h in hits:
        if len(out) >= limit:
            break
        name = (h.get('name') or '').split('·')[0].strip().lower()  # coupe "· lot x50"
        if name and name not in seen and ql in name:
            seen.add(name); out.append(name)

    return out[:limit]


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def admin_categories(request):
    if request.method == 'GET':
        cats = Category.objects.select_related('parent').order_by('sort_order', 'name')
        return Response([_cat_dict(c) for c in cats])
    return _save_category(request, None)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def admin_category_detail(request, pk):
    try:
        cat = Category.objects.select_related('parent').get(id=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Catégorie introuvable'}, status=404)
    if request.method == 'DELETE':
        cat.delete()
        return Response(status=204)
    if request.method == 'GET':
        return Response(_cat_dict(cat))
    return _save_category(request, cat)


# ── Admin : bannière de recherche d'une catégorie ─────────────────
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def admin_category_banner(request, pk):
    """
    GET    → {banner_url, banner_link}
    POST   → enregistre : soit un fichier (banner_image → upload storage),
             soit une URL (banner_url, galerie), + banner_link.
    DELETE → vide la bannière.
    """
    try:
        cat = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Catégorie introuvable'}, status=404)

    if request.method == 'GET':
        return Response({'banner_url': cat.banner_url, 'banner_link': cat.banner_link})

    if request.method == 'DELETE':
        cat.banner_url = ''
        cat.banner_link = ''
        cat.save(update_fields=['banner_url', 'banner_link'])
        return Response(status=204)

    # POST
    data = request.data
    banner_url = data.get('banner_url', '') or cat.banner_url

    f = request.FILES.get('banner_image')
    if f is not None:
        ext  = os.path.splitext(f.name)[1].lower() or '.jpg'
        key  = f'categories/banners/{_uuid.uuid4().hex}{ext}'
        path = default_storage.save(key, ContentFile(f.read()))
        url  = default_storage.url(path)
        if url.startswith('/'):
            url = request.build_absolute_uri(url)
        banner_url = url

    cat.banner_url  = banner_url
    cat.banner_link = data.get('banner_link', '') or ''
    cat.save(update_fields=['banner_url', 'banner_link'])
    return Response({'banner_url': cat.banner_url, 'banner_link': cat.banner_link})


# ── Recommandations (sous profil boutique) ────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def product_recommendations(request, pk):
    """
    'Accessoires recommandés' : même catégorie en priorité,
    sinon fallback sur d'autres produits du même fournisseur.
    """
    try:
        product = Product.objects.select_related('supplier', 'category').get(id=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    LIMIT = 8

    results = list(
        Product.objects.filter(
            status='approved',
            category=product.category,
        ).exclude(id=pk).select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related('images', 'price_tiers').order_by('-sold_count')[:LIMIT]
    )

    if len(results) < LIMIT:
        existing_ids = [p.id for p in results] + [product.id]
        remaining = LIMIT - len(results)
        fallback = Product.objects.filter(
            status='approved',
            supplier=product.supplier,
        ).exclude(id__in=existing_ids).select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related('images', 'price_tiers').order_by('-sold_count')[:remaining]
        results += list(fallback)

    serializer = ProductListSerializer(results, many=True)
    return Response(serializer.data)


# ── Recommandés (perso) ───────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_products(request):

    if request.user.is_authenticated:
        from store.models import ProductInteraction
        from django.db.models import Count

        top_categories = ProductInteraction.objects.filter(
            user=request.user
        ).values('product__category').annotate(
            count=Count('product__category')
        ).order_by('-count')[:3]

        category_ids = [
            c['product__category'] for c in top_categories
            if c['product__category']
        ]

        if category_ids:
            products = Product.objects.filter(
                status='approved',
                category_id__in=category_ids,
            ).select_related(
                'supplier', 'supplier__store', 'category'
            ).prefetch_related('images').order_by('-sold_count')[:30]

            if products.exists():
                serializer = ProductListSerializer(products, many=True)
                return Response({'results': serializer.data, 'personalized': True})

    products = Product.objects.filter(
        status='approved'
    ).select_related(
        'supplier', 'supplier__store', 'category'
    ).prefetch_related('images').order_by('-sold_count')[:30]

    serializer = ProductListSerializer(products, many=True)
    return Response({'results': serializer.data, 'personalized': False})


# ── Suggestions de recherche ──────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):

    query = request.query_params.get('q', '').strip()
    if len(query) < 2:
        return Response({'suggestions': []})

    product_names = Product.objects.filter(
        status='approved', name__icontains=query,
    ).order_by('-sold_count').values_list('name', flat=True).distinct()[:5]

    category_names = Category.objects.filter(
        name__icontains=query, is_active=True,
    ).values_list('name', flat=True)[:3]

    suggestions = []
    for name in product_names:
        suggestions.append({'text': name, 'type': 'product'})
    for name in category_names:
        suggestions.append({'text': name, 'type': 'category'})

    return Response({'suggestions': suggestions[:8]})


# ── Tendances ─────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def trending_products(request):
    products = Product.objects.filter(
        status='approved'
    ).select_related(
        'supplier', 'supplier__store', 'category'
    ).prefetch_related('images').order_by(
        '-badge_flash', '-rating_avg', '-sold_count'
    )[:15]
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


# ── Products List ─────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def products_list(request):

    products = Product.objects.filter(
        status='approved'
    ).select_related(
        'supplier', 'supplier__store', 'category'
    ).prefetch_related('images')

    category = request.query_params.get('category')
    if category:
        products = products.filter(category__slug=category)

    supplier = request.query_params.get('supplier')
    if supplier:
        products = products.filter(supplier__slug=supplier)

    badge = request.query_params.get('badge')
    if badge == 'flash':
        products = products.filter(badge_flash=True)
    elif badge == 'choice':
        products = products.filter(badge_choice=True)

    sort = request.query_params.get('sort', '-sold_count')
    ALLOWED_SORTS = [
        'sold_count', '-sold_count',
        'base_price_tnd', '-base_price_tnd',
        'created_at', '-created_at',
        'rating_avg', '-rating_avg',
    ]
    if sort in ALLOWED_SORTS:
        products = products.order_by(sort)

    limit  = min(int(request.query_params.get('limit', 18)), 100)
    offset = int(request.query_params.get('offset', 0))
    total  = products.count()
    products = products[offset:offset + limit]

    serializer = ProductListSerializer(products, many=True)
    return Response({
        'total': total, 'limit': limit, 'offset': offset,
        'results': serializer.data,
    })


# ── Product Detail ────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = Product.objects.select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related(
            'images', 'price_tiers', 'variants', 'choice_groups__variants'
        ).get(id=pk, status='approved')
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

    Product.objects.filter(id=pk).update(view_count=product.view_count + 1)

    if request.user.is_authenticated:
        from store.models import ProductInteraction
        ProductInteraction.objects.create(
            user=request.user, product=product, event_type='view',
        )

    # ⭐ context={'request': request} → nécessaire pour is_favorited
    serializer = ProductDetailSerializer(product, context={'request': request})
    return Response(serializer.data)


# ── Search (via Meilisearch — tolérant aux fautes) ────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):

    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Paramètre q obligatoire.'}, status=400)

    from . import search as meili

    # 1) Meilisearch renvoie les IDs correspondants (fuzzy), classés par pertinence
    try:
        res = meili.get_index().search(query, {
            'limit': 40,
            'attributesToRetrieve': ['id'],
        })
        ids = [h['id'] for h in res.get('hits', [])]
    except Exception:
        ids = None   # Meilisearch down → fallback Postgres plus bas

    if ids is not None:
        # 2) On recharge les produits complets depuis Postgres (pour la sérialisation)
        products_qs = Product.objects.filter(
            status='approved', id__in=ids,
        ).select_related('supplier', 'supplier__store', 'category').prefetch_related('images')

        # 3) On respecte l'ordre de pertinence de Meilisearch
        by_id = {str(p.id): p for p in products_qs}
        products = [by_id[i] for i in ids if i in by_id]
    else:
        # Fallback : ancienne recherche Postgres si Meilisearch est éteint
        products = list(Product.objects.filter(
            status='approved'
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(supplier__company_name__icontains=query)
        ).select_related('supplier', 'supplier__store', 'category').prefetch_related('images').order_by('-sold_count')[:20])

    if request.user.is_authenticated:
        from store.models import SearchHistory
        SearchHistory.objects.create(
            user=request.user, query=query, result_count=len(products),
        )

    serializer = ProductListSerializer(products[:20], many=True)
    return Response({'query': query, 'total': len(products), 'results': serializer.data})


# ── Similar Products ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def similar_products(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    similar = Product.objects.filter(
        status='approved', category=product.category,
    ).exclude(id=pk).select_related(
        'supplier', 'category'
    ).prefetch_related('images').order_by('-sold_count')[:10]

    serializer = ProductListSerializer(similar, many=True)
    return Response(serializer.data)


# ── Reviews ───────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def product_reviews(request, pk):
    reviews = Review.objects.filter(
        product_id=pk
    ).select_related('reviewer', 'variant').prefetch_related('photos').order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    '''
    POST /api/products/reviews/create/
    body: { product_id, rating, comment?, order_id?, variant_id?, photos?[] }

    Achat vérifié : l'acheteur doit avoir une commande LIVRÉE contenant
    le produit. Un seul avis par (acheteur, produit) — contrainte DB.
    '''
    from .serializers import ReviewCreateSerializer  # évite les imports circulaires si besoin

    s = ReviewCreateSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    data = s.validated_data

    try:
        product = Product.objects.select_related('supplier').get(id=data['product_id'])
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    # ── Achat vérifié : au moins un OrderItem livré pour ce produit ──
    from orders.models import OrderItem
    has_delivered = OrderItem.objects.filter(
        product=product,
        sub_order__status='delivered',
        sub_order__order__buyer=request.user,
    ).exists()
    if not has_delivered:
        return Response(
            {'error': "Vous ne pouvez évaluer qu'un produit reçu."},
            status=403
        )

    # ── Déjà évalué ? (la contrainte DB le bloquerait, on renvoie un message clair) ──
    if Review.objects.filter(reviewer=request.user, product=product).exists():
        return Response({'error': 'Vous avez déjà évalué ce produit.'}, status=409)

    review = Review.objects.create(
        reviewer   = request.user,
        product    = product,
        supplier   = product.supplier,
        order_id   = data.get('order_id') or None,
        variant_id = data.get('variant_id') or None,
        rating     = data['rating'],
        comment    = data.get('comment', ''),
    )

    for i, url in enumerate(data.get('photos', [])):
        ReviewPhoto.objects.create(review=review, url=url, sort_order=i)

    # ── Recalcule rating_avg / rating_count du produit (1 requête agrégée) ──
    agg = Review.objects.filter(product=product).aggregate(
        avg=Avg('rating'), n=Count('id')
    )
    product.rating_avg   = round(agg['avg'] or 0, 2)
    product.rating_count = agg['n'] or 0
    product.save(update_fields=['rating_avg', 'rating_count'])

    return Response(ReviewSerializer(review).data, status=201)


# ══════════════════════════════════════════════════════════════════
#  FAVORIS (acheteur)
# ══════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def favorites(request):
    """GET = liste des favoris · POST {product_id} = ajoute."""
    if request.method == 'GET':
        favs = (
            Favorite.objects
            .filter(user=request.user)
            .select_related('product__supplier__store', 'product__category')
            .prefetch_related('product__images', 'product__price_tiers')
        )
        products = [f.product for f in favs]
        data = ProductListSerializer(products, many=True, context={'request': request}).data
        return Response({'products': data, 'suppliers': []})

    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'product_id requis'}, status=400)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    Favorite.objects.get_or_create(user=request.user, product=product)
    return Response({'ok': True, 'product_id': str(product_id)}, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def favorite_detail(request, product_id):
    """DELETE = retire ce produit des favoris (idempotent)."""
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    return Response(status=204)


# ══════════════════════════════════════════════════════════════════
#  ESPACE FOURNISSEUR (écriture)
# ══════════════════════════════════════════════════════════════════

# ── Création d'un produit ─────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': "Compte fournisseur requis."}, status=403)
    ser = ProductCreateSerializer(data=request.data, context={'request': request})
    ser.is_valid(raise_exception=True)
    p = ser.save()
    return Response({'id': str(p.id), 'slug': p.slug, 'status': p.status}, status=201)

# ── Upload d'une image produit ────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_product_image(request):
    f = request.FILES.get('file')
    if not f:
        return Response({'error': 'Aucun fichier.'}, status=400)
    if f.content_type not in {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}:
        return Response({'error': 'Format non supporté (png, jpg, jpeg, webp).'}, status=400)
    if f.size > 5 * 1024 * 1024:
        return Response({'error': 'Fichier trop volumineux (max 5 Mo).'}, status=400)

    # ── Optimisation : resize + conversion WebP ──
    img = Image.open(f)
    img = img.convert('RGB') if img.mode in ('RGBA', 'P') else img
    img.thumbnail((1200, 1200))

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=80)
    buffer.seek(0)

    key = f"products/{_uuid.uuid4().hex}.webp"

    # InMemoryUploadedFile expose content_type explicitement, contrairement à
    # ContentFile — nécessaire pour que le storage (Supabase/S3) envoie le bon
    # Content-Type au lieu de retomber sur application/octet-stream.
    upload_file = InMemoryUploadedFile(
        buffer, 'ImageField', key, 'image/webp',
        buffer.getbuffer().nbytes, None
    )

    path = default_storage.save(key, upload_file)
    url = default_storage.url(path)
    if url.startswith('/'):
        url = request.build_absolute_uri(url)
    return Response({'url': url}, status=201)
# ── Upload + compression d'une vidéo produit ──────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_product_video(request):
    f = request.FILES.get('file')
    if not f:
        return Response({'error': 'Aucun fichier.'}, status=400)

    allowed = {'video/mp4', 'video/webm', 'video/quicktime',
               'video/x-matroska', 'video/x-msvideo'}
    if f.content_type not in allowed:
        return Response({'error': 'Format non supporté (mp4, webm, mov, mkv, avi).'}, status=400)
    if f.size > 100 * 1024 * 1024:
        return Response({'error': 'Vidéo trop volumineuse (max 100 Mo).'}, status=400)

    if not shutil.which('ffmpeg'):
        return Response({'error': "Compression vidéo indisponible (ffmpeg non installé)."}, status=503)

    tmp_dir     = tempfile.mkdtemp(prefix='vid_')
    suffix      = os.path.splitext(f.name)[1].lower() or '.mp4'
    in_path     = os.path.join(tmp_dir, f'in{suffix}')
    out_path    = os.path.join(tmp_dir, 'out.mp4')
    poster_path = os.path.join(tmp_dir, 'poster.webp')

    try:
        with open(in_path, 'wb') as dst:
            for chunk in f.chunks():
                dst.write(chunk)

        # Transcodage : H.264 ≤720p, CRF 28, faststart, AAC, coupé à 60 s max.
        subprocess.run([
            'ffmpeg', '-y', '-i', in_path,
            '-t', '60',
            '-vf', "scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease,"
                   "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '96k',
            '-movflags', '+faststart',
            out_path,
        ], check=True, capture_output=True, timeout=180)

        # Poster (frame à 1 s) — best effort.
        try:
            subprocess.run([
                'ffmpeg', '-y', '-ss', '1', '-i', out_path,
                '-frames:v', '1', poster_path,
            ], check=True, capture_output=True, timeout=60)
        except subprocess.SubprocessError:
            pass

        def _store(local_path, key, content_type, field):
            with open(local_path, 'rb') as fh:
                buf = BytesIO(fh.read())
            up = InMemoryUploadedFile(buf, field, key, content_type, buf.getbuffer().nbytes, None)
            path = default_storage.save(key, up)
            url = default_storage.url(path)
            return request.build_absolute_uri(url) if url.startswith('/') else url

        video_url = _store(out_path, f"products/videos/{_uuid.uuid4().hex}.mp4", 'video/mp4', 'FileField')

        poster_url = ''
        if os.path.exists(poster_path) and os.path.getsize(poster_path) > 0:
            poster_url = _store(poster_path, f"products/videos/{_uuid.uuid4().hex}.webp", 'image/webp', 'ImageField')

        return Response({'url': video_url, 'poster': poster_url}, status=201)

    except subprocess.TimeoutExpired:
        return Response({'error': "Traitement trop long, réessaie avec une vidéo plus courte."}, status=400)
    except subprocess.CalledProcessError:
        return Response({'error': "Vidéo illisible ou corrompue."}, status=400)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
# ── Mes produits (liste fournisseur) ──────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_products(request):
    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': 'Compte fournisseur requis.'}, status=403)
    qs = Product.objects.filter(
        supplier=request.user.supplier_profile
    ).select_related('category').prefetch_related('images').order_by('-created_at')
    st = request.query_params.get('status')
    if st:
        qs = qs.filter(status=st)
    return Response(SupplierProductSerializer(qs, many=True).data)