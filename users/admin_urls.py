# users/admin_urls.py  (NOUVEAU FICHIER)
# Monté sous /api/admin/ dans le urls.py RACINE (voir instructions).
from django.urls import path
from . import admin_views

urlpatterns = [
    path('auth/login/',  admin_views.admin_login,  name='admin-login'),
    path('auth/logout/', admin_views.admin_logout, name='admin-logout'),
]