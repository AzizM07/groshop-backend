from django.urls import path
from . import views

urlpatterns = [
    # ── Racine + recherche ──
    path('',              views.products_list,      name='products-list'),
    path('search/',       views.search_products,    name='search-products'),
    path('suggestions/',  views.search_suggestions, name='search-suggestions'),
    path('trending/',     views.trending_products,  name='trending-products'),
    path('recommended/',  views.recommended_products, name='recommended-products'),
    path('categories/',   views.categories_list,    name='categories-list'),

    # ── Espace fournisseur (routes statiques AVANT <uuid:pk>) ──
    path('create/',       views.create_product,       name='product-create'),
    path('upload-image/', views.upload_product_image, name='product-upload-image'),
    path('mine/',         views.my_products,          name='product-mine'),

    # ── Détail produit (UUID) — doit rester en dernier ──
    path('<uuid:pk>/',                 views.product_detail,          name='product-detail'),
    path('<uuid:pk>/similar/',         views.similar_products,        name='similar-products'),
    path('<uuid:pk>/reviews/',         views.product_reviews,         name='product-reviews'),
    path('<uuid:pk>/recommendations/', views.product_recommendations, name='product-recommendations'),
]