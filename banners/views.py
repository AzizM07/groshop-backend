from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage

from .models import Banner, BannerImage, HeroLayout
from .serializers import BannerSerializer, BannerImageSerializer, HeroLayoutSerializer


# ── Admin CRUD ────────────────────────────────────────────────────
class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAdminUser]   # seul un admin peut modifier


# ── Public : bannières actives ──────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def active_banners(request):
    banners = Banner.objects.filter(is_active=True).order_by('zone', 'position')
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data)


# ── Galerie d'une bannière (admin) ──────────────────────────────
@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def add_banner_image(request, banner_id):
    try:
        banner = Banner.objects.get(id=banner_id)
    except Banner.DoesNotExist:
        return Response({'error': 'Bannière introuvable'}, status=status.HTTP_404_NOT_FOUND)

    image_file = request.FILES.get('image')
    image_url_ext = request.data.get('image_url_ext', '')
    if not image_file and not image_url_ext:
        return Response({'error': 'image ou image_url_ext requis'}, status=status.HTTP_400_BAD_REQUEST)

    next_pos = banner.gallery_images.count()
    img = BannerImage.objects.create(
        banner=banner,
        image=image_file,
        image_url_ext=image_url_ext,
        position=next_pos,
    )
    return Response(BannerImageSerializer(img).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_banner_image(request, banner_id, image_id):
    try:
        img = BannerImage.objects.get(id=image_id, banner_id=banner_id)
    except BannerImage.DoesNotExist:
        return Response({'error': 'Image introuvable'}, status=status.HTTP_404_NOT_FOUND)
    img.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Layout : actif (public) ─────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def active_layout(request):
    layout = HeroLayout.objects.filter(is_active=True).first()
    if layout:
        serializer = HeroLayoutSerializer(layout)
        return Response(serializer.data)
    # Fallback : layout par défaut "two_cards"
    default = HeroLayout.objects.filter(code='two_cards').first()
    if default:
        return Response(HeroLayoutSerializer(default).data)
    return Response({'code': 'two_cards', 'grid_style': '2fr 1fr'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_media(request):
    """Liste les images d'un dossier du bucket, via le storage Django (= Supabase)."""
    folder = request.GET.get('folder', 'banners')
    try:
        _dirs, files = default_storage.listdir(folder)
    except Exception:
        files = []
    items = [
        {'name': name, 'url': default_storage.url(f'{folder}/{name}')}
        for name in files
        if name  # ignore les entrées vides
    ]
    return Response(items)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_layouts(request):
    """Liste tous les layouts (admin)."""
    layouts = HeroLayout.objects.all()
    serializer = HeroLayoutSerializer(layouts, many=True)
    return Response(serializer.data)


# ── Layout : changer (admin) ────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAdminUser])
def set_active_layout(request):
    layout_id = request.data.get('layout_id')
    if not layout_id:
        return Response({'error': 'layout_id requis'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        layout = HeroLayout.objects.get(id=layout_id)
    except HeroLayout.DoesNotExist:
        return Response({'error': 'Layout non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    HeroLayout.objects.update(is_active=False)
    layout.is_active = True
    layout.save()
    return Response(HeroLayoutSerializer(layout).data)