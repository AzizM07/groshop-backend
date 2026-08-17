from django.urls import path
from . import views
from . import access_views
urlpatterns = [
    # ── Racine + recherche ──
    path('',              views.products_list,      name='products-list'),
    path('search/',       views.search_products,    name='search-products'),
    path('suggestions/',  views.search_suggestions, name='search-suggestions'),
    path('trending/',     views.trending_products,  name='trending-products'),
    path('recommended/',  views.recommended_products, name='recommended-products'),
    path('categories/',   views.categories_list,    name='categories-list'),
    path('admin/categories/',           views.admin_categories,       name='admin-categories'),
    path('admin/categories/<uuid:pk>/', views.admin_category_detail,  name='admin-category-detail'),
    path('category-banner/', views.category_banner, name='category-banner'),
    path('admin/categories/<uuid:pk>/banner/', views.admin_category_banner, name='admin-category-banner'),
    # ── Favoris acheteur (routes statiques AVANT <uuid:pk>) ──
    path('favorites/',                   views.favorites,       name='favorites'),
    path('favorites/<uuid:product_id>/', views.favorite_detail, name='favorite-detail'),

    # ── Espace fournisseur (routes statiques AVANT <uuid:pk>) ──
    path('create/',       views.create_product,       name='product-create'),
    path('upload-image/', views.upload_product_image, name='product-upload-image'),
    path('upload-video/', views.upload_product_video),
    path('mine/',         views.my_products,          name='product-mine'),
    path('products/categories/for-you/', views.categories_for_you),
    # ── Détail produit (UUID) — doit rester en dernier ──
    path('reviews/create/', views.create_review, name='review-create'),
    path('autocomplete/', views.search_autocomplete, name='search-autocomplete'),
    path('<uuid:pk>/',                 views.product_detail,          name='product-detail'),
    path('<uuid:pk>/similar/',         views.similar_products,        name='similar-products'),
    path('<uuid:pk>/reviews/',         views.product_reviews,         name='product-reviews'),
    path('<uuid:pk>/recommendations/', views.product_recommendations, name='product-recommendations'),
    # ── Accès prix masqués ──
    path('access/check/<uuid:user_id>/',                      access_views.check_access,              name='access-check'),
    path('access/my-unlocks/',                                access_views.my_unlocks,                name='access-my-unlocks'),
    path('access/unlock-supplier/<uuid:user_id>/',            access_views.unlock_supplier_for_user,  name='access-unlock-supplier'),
    path('access/unlock-product/<uuid:product_id>/',          access_views.unlock_product_for_user,   name='access-unlock-product'),
    path('access/revoke-supplier/<uuid:unlock_id>/',          access_views.revoke_supplier_unlock,    name='access-revoke-supplier'),
    path('access/revoke-product/<uuid:unlock_id>/',           access_views.revoke_product_unlock,     name='access-revoke-product'),
    ]