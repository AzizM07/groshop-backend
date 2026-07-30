# groshop/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',             admin.site.urls),
    path('api/auth/',          include('users.urls')),
    path('api/notifications/', include('notifications.urls')),
    # ── Espace admin/CEO (Bearer / IsAdmin), tout sous /api/admin/ ──
    path('api/admin/',         include('users.admin_urls')),    # auth : login / logout
    path('api/admin/',         include('orders.admin_urls')),   # stats + commandes (lecture)
    path('api/', include('banners.urls')),
    path('api/products/',      include('products.urls')),
    path('api/orders/',        include('orders.urls')),
    path('api/cart/',          include('orders.cart_urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/messaging/',     include('messaging.urls')),
    path('api/gamification/',  include('gamification.urls')),
    path('api/store/',         include('store.urls')),
    path('api/analytics/',     include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)