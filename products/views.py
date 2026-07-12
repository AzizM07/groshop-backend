from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer
)


# ── Categories ────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list(request):
    # Seulement les catégories racines (parent=None)
    # Les enfants sont imbriqués via get_children()
    categories = Category.objects.filter(
        parent=None, is_active=True
    ).prefetch_related('children')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# ── À ajouter dans products/views.py ──

@api_view(['GET'])
@permission_classes([AllowAny])
def product_recommendations(request, pk):
    """
    'Accessoires recommandés' sous le profil boutique.
    Logique : produits de la même catégorie en priorité,
    sinon fallback sur d'autres produits du même fournisseur.
    """
    try:
        product = Product.objects.select_related('supplier', 'category').get(id=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    LIMIT = 8

    # ── 1. Priorité : même catégorie (hors ce produit) ──
    results = list(
        Product.objects.filter(
            status='approved',
            category=product.category,
        ).exclude(
            id=pk
        ).select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related('images', 'price_tiers').order_by('-sold_count')[:LIMIT]
    )

    # ── 2. Fallback : complète avec d'autres produits du même fournisseur ──
    if len(results) < LIMIT:
        existing_ids = [p.id for p in results] + [product.id]
        remaining = LIMIT - len(results)

        fallback = Product.objects.filter(
            status='approved',
            supplier=product.supplier,
        ).exclude(
            id__in=existing_ids
        ).select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related('images', 'price_tiers').order_by('-sold_count')[:remaining]

        results += list(fallback)

    serializer = ProductListSerializer(results, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def recommended_products(request):

    if request.user.is_authenticated:
        from store.models import ProductInteraction
        from django.db.models import Count

        # Catégories les plus consultées par cet utilisateur
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
                return Response({
                    'results':     serializer.data,
                    'personalized': True,
                })

    # Fallback — non connecté ou pas d'historique
    products = Product.objects.filter(
        status='approved'
    ).select_related(
        'supplier', 'supplier__store', 'category'
    ).prefetch_related('images').order_by('-sold_count')[:30]

    serializer = ProductListSerializer(products, many=True)
    return Response({
        'results':     serializer.data,
        'personalized': False,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):

    query = request.query_params.get('q', '').strip()

    if len(query) < 2:
        return Response({'suggestions': []})

    # Noms de produits qui matchent
    product_names = Product.objects.filter(
        status='approved',
        name__icontains=query,
    ).order_by('-sold_count').values_list('name', flat=True).distinct()[:5]

    # Noms de catégories qui matchent
    category_names = Category.objects.filter(
        name__icontains=query,
        is_active=True,
    ).values_list('name', flat=True)[:3]

    suggestions = []

    for name in product_names:
        suggestions.append({'text': name, 'type': 'product'})

    for name in category_names:
        suggestions.append({'text': name, 'type': 'category'})

    return Response({'suggestions': suggestions[:8]})

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_products(request):
    # Approximation "tendance" : flash sales + meilleures notes + ventes
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

    # ── Filtres optionnels depuis l'URL ──
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

    # ── Tri ──
    sort = request.query_params.get('sort', '-sold_count')
    ALLOWED_SORTS = [
        'sold_count', '-sold_count',
        'base_price_tnd', '-base_price_tnd',
        'created_at', '-created_at',
        'rating_avg', '-rating_avg',
    ]
    if sort in ALLOWED_SORTS:
        products = products.order_by(sort)

    # ── Pagination simple ──
    limit  = min(int(request.query_params.get('limit', 18)), 100)
    offset = int(request.query_params.get('offset', 0))
    total  = products.count()
    products = products[offset:offset + limit]

    serializer = ProductListSerializer(products, many=True)
    return Response({
        'total':    total,
        'limit':    limit,
        'offset':   offset,
        'results':  serializer.data,
    })


# ── Product Detail — MISE À JOUR (ajoute 'variants' au prefetch) ──
@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, pk):
 
    try:
        product = Product.objects.select_related(
            'supplier', 'supplier__store', 'category'
        ).prefetch_related(
            'images', 'price_tiers', 'variants'   # ← AJOUTE 'variants'
        ).get(id=pk, status='approved')
    except Product.DoesNotExist:
        return Response(
            {'error': 'Produit non trouvé.'},
            status=status.HTTP_404_NOT_FOUND
        )
 
    # Incrémente le compteur de vues
    Product.objects.filter(id=pk).update(view_count=product.view_count + 1)
 
    # Enregistre l'interaction si connecté
    if request.user.is_authenticated:
        from store.models import ProductInteraction
        ProductInteraction.objects.create(
            user=request.user,
            product=product,
            event_type='view',
        )
 
    serializer = ProductDetailSerializer(product)
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

    # Sauvegarde la recherche si connecté
    if request.user.is_authenticated:
        from store.models import SearchHistory
        SearchHistory.objects.create(
            user         = request.user,
            query        = query,
            result_count = products.count(),
        )

    serializer = ProductListSerializer(products[:20], many=True)
    return Response({
        'query':   query,
        'total':   products.count(),
        'results': serializer.data,
    })


# ── Similar Products ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def similar_products(request, pk):
    # Produits de la même catégorie
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    similar = Product.objects.filter(
        status='approved',
        category=product.category,
    ).exclude(
        id=pk
    ).select_related(
        'supplier', 'category'
    ).prefetch_related('images').order_by('-sold_count')[:10]

    serializer = ProductListSerializer(similar, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_reviews(request, pk):
 
    reviews = Review.objects.filter(
        product_id=pk
    ).select_related('reviewer', 'variant').prefetch_related('photos').order_by('-created_at')
 
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
 