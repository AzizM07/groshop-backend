from django.contrib import admin
from .models import Banner, HeroLayout

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'zone', 'position', 'is_active']
    list_filter = ['zone', 'is_active']
    search_fields = ['title', 'tag']

@admin.register(HeroLayout)
class HeroLayoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_editable = ['is_active']