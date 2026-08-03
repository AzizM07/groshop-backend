# users/admin.py
from django.contrib import admin
from django.apps import apps

from .models import BannedPhone

# ── Admin dédié pour bannir un numéro (recherche + colonnes utiles) ──
# Déclaré AVANT la boucle : la boucle le sautera via AlreadyRegistered.
@admin.register(BannedPhone)
class BannedPhoneAdmin(admin.ModelAdmin):
    list_display  = ('phone', 'reason', 'banned_at')
    search_fields = ('phone',)
    ordering      = ('-banned_at',)


# ── Enregistre automatiquement tous les autres modèles de l'app users ──
# (User, BuyerProfile, SupplierProfile, PhoneOTP, …)
for model in apps.get_app_config('users').get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass