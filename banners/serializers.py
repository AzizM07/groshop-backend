from rest_framework import serializers
from .models import Banner, BannerImage, HeroLayout


class BannerImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = BannerImage
        fields = ['id', 'url', 'position']

    def get_url(self, obj):
        if obj.image_url_ext:
            return obj.image_url_ext
        if obj.image:
            return obj.image.url
        return None


class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    # Liste d'URLs simples, consommée telle quelle par le frontend public (HeroGrid).
    # Si la bannière a une galerie, elle prime sur l'image de couverture.
    images = serializers.SerializerMethodField()

    # Version détaillée (avec id) pour l'admin, qui a besoin de savoir quelle
    # image supprimer/réordonner.
    image_objects = BannerImageSerializer(source='gallery_images', many=True, read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'tag', 'subtitle', 'cta_label', 'link',
            'image', 'image_url', 'image_url_ext', 'images', 'image_objects',
            'tint_from', 'tint_to',
            'zone', 'position', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image_url_ext:      # image de la galerie Supabase (cover)
            return obj.image_url_ext
        if obj.image:              # fichier téléversé (cover)
            return obj.image.url
        return None

    def get_images(self, obj):
        gallery = obj.gallery_images.order_by('position')
        urls = [
            (img.image_url_ext or (img.image.url if img.image else None))
            for img in gallery
        ]
        urls = [u for u in urls if u]
        if urls:
            return urls
        cover = self.get_image_url(obj)
        return [cover] if cover else []


class HeroLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroLayout
        fields = ['id', 'name', 'code', 'grid_style', 'is_active']