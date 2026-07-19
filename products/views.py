import os
import uuid as _uuid

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, F, Exists, OuterRef

from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Category, Product, Review, ReviewPhoto, Favorite   # ← Favorite ajouté
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer,
    ProductCreateSerializer, SupplierProductSerializer,
)


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
            'images', 'price_tiers', 'variants'
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


# ── Search ────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):

    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Paramètre q obligatoire.'}, status=400)

    products = Product.objects.filter(
        status='approved'
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(supplier__company_name__icontains=query)
    ).select_related(
        'supplier', 'supplier__store', 'category'
    ).prefetch_related('images').order_by('-sold_count')

    if request.user.is_authenticated:
        from store.models import SearchHistory
        SearchHistory.objects.create(
            user=request.user, query=query, result_count=products.count(),
        )

    serializer = ProductListSerializer(products[:20], many=True)
    return Response({'query': query, 'total': products.count(), 'results': serializer.data})


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

    ext  = os.path.splitext(f.name)[1].lower() or '.jpg'
    key  = f"products/{_uuid.uuid4().hex}{ext}"
    path = default_storage.save(key, ContentFile(f.read()))
    url  = default_storage.url(path)
    if url.startswith('/'):
        url = request.build_absolute_uri(url)
    return Response({'url': url}, status=201)


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