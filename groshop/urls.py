# groshop/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',             admin.site.urls),
    path('api/auth/',          include('users.urls')),
    path('api/products/',      include('products.urls')),
    path('api/orders/',        include('orders.urls')),
    path('api/cart/',          include('orders.cart_urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/messaging/',     include('messaging.urls')),
    path('api/gamification/',  include('gamification.urls')),
    path('api/store/',         include('store.urls')),
]