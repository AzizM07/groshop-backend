from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BannerViewSet,
    active_banners,
    add_banner_image,
    delete_banner_image,
    active_layout,
    all_layouts,
    set_active_layout,
    list_media,
)

router = DefaultRouter()
router.register(r'banners', BannerViewSet, basename='banner')

urlpatterns = [
    # ⚠️ IMPORTANT : ces chemins doivent être déclarés AVANT include(router.urls).
    # Le router DRF génère 'banners/<pk>/' avec un pk qui matche n'importe quelle
    # chaîne — si 'banners/active/' est déclaré après, Django le fait matcher par
    # 'banners/<pk>/' (pk="active") en premier, ce qui tombe sur BannerViewSet.retrieve
    # et sa permission IsAdminUser → 401 pour un utilisateur non connecté.

    # Public
    path('banners/active/', active_banners, name='active-banners'),
    path('layout/active/', active_layout, name='active-layout'),

    # Galerie d'une bannière (admin)
    path('banners/<int:banner_id>/images/', add_banner_image, name='add-banner-image'),
    path('banners/<int:banner_id>/images/<int:image_id>/', delete_banner_image, name='delete-banner-image'),

    # Layouts (admin)
    path('admin/layouts/', all_layouts, name='all-layouts'),
    path('layout/set/', set_active_layout, name='set-active-layout'),

    # Médiathèque (admin)
    path('admin/media/', list_media, name='list-media'),

    # Router en dernier : ses routes génériques ('banners/', 'banners/<pk>/')
    # ne doivent jamais passer avant les chemins spécifiques ci-dessus.
    path('', include(router.urls)),
]

# NOTE : ce fichier suppose qu'il est inclus depuis le urls.py racine sous le
# préfixe 'api/', comme le laissent penser les appels du frontend
# ('/api/layout/active/', '/api/banners/active/' dans HeroGrid.jsx).
# Si ton urls.py existant a des noms de routes ou un préfixe différents,
# ajuste en conséquence plutôt que d'écraser tel quel.