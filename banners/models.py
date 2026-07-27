from django.db import models


class Banner(models.Model):
    ZONES = (
        ('hero_slider', 'Hero Slider'),
        ('side_card', 'Side Card'),
    )

    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=100, blank=True, default='')
    subtitle = models.CharField(max_length=255, blank=True, default='')
    cta_label = models.CharField(max_length=50, blank=True, default='')
    link = models.URLField(blank=True, null=True)

    # Image de couverture (rétro-compatible avec l'ancien modèle single-image)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    image_url_ext = models.URLField(blank=True, default='')  # image choisie dans la galerie

    tint_from = models.CharField(max_length=6, blank=True, default='')
    tint_to = models.CharField(max_length=6, blank=True, default='')

    zone = models.CharField(max_length=20, choices=ZONES, default='hero_slider')
    position = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['zone', 'position']
        unique_together = ['zone', 'position']

    def __str__(self):
        return self.title


class BannerImage(models.Model):
    """Image supplémentaire d'une bannière, pour le carrousel interne à la carte.
    Si une bannière a plusieurs BannerImage, le frontend affiche une pastille
    de navigation et fait défiler ces images automatiquement.
    """
    banner = models.ForeignKey(Banner, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banners/gallery/', blank=True, null=True)
    image_url_ext = models.URLField(blank=True, default='')  # image choisie dans la galerie Supabase
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.banner.title} — image {self.position}"


class HeroLayout(models.Model):
    LAYOUTS = (
        ('two_cards', '2 cartes (2fr 1fr)'),
        ('three_cards', '3 cartes (1fr 1fr 1fr)'),
        ('full_width', 'Pleine largeur (1fr)'),
        ('two_rows', '2 rangées (1fr 1fr)'),
        ('one_big', 'Grande + petite (3fr 1fr)'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, choices=LAYOUTS, unique=True)
    grid_style = models.CharField(max_length=50, help_text="ex: '2fr 1fr'")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name