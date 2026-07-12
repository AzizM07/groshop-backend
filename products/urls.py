from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.products_list,       name='products-list'),
    path('search/',                 views.search_products,     name='search-products'),
    path('suggestions/',            views.search_suggestions,  name='search-suggestions'),  # ← avant pk
    path('trending/',                views.trending_products,   name='trending-products'),
    path('recommended/',             views.recommended_products,name='recommended-products'),
    path('categories/',             views.categories_list,     name='categories-list'),
    path('<uuid:pk>/',              views.product_detail,      name='product-detail'),
    path('<uuid:pk>/similar/',      views.similar_products,    name='similar-products'),
    path('<uuid:pk>/reviews/',      views.product_reviews,      name='product-reviews'),
    path('<uuid:pk>/recommendations/', views.product_recommendations, name='product-recommendations'),

]