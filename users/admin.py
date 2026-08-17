# users/admin.py
from django.contrib import admin, messages
from django.apps import apps
from django.utils import timezone

from .models import BannedPhone, User


# ── Admin dédié pour bannir un numéro (recherche + colonnes utiles) ──
# Déclaré AVANT la boucle : la boucle le sautera via AlreadyRegistered.
@admin.register(BannedPhone)
class BannedPhoneAdmin(admin.ModelAdmin):
    list_display  = ('phone', 'reason', 'banned_at')
    search_fields = ('phone',)
    ordering      = ('-banned_at',)


# ══════════════════════════════════════════════════════════════════
#  USER — avec actions de vérification boutique
# ══════════════════════════════════════════════════════════════════
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = (
        'email', 'full_name', 'role', 'is_active', 'is_verified',
        'business_status', 'business_name', 'created_at',
    )
    list_filter   = ('role', 'is_active', 'is_verified', 'business_status', 'created_at')
    search_fields = ('email', 'full_name', 'phone', 'business_name', 'business_rne')
    ordering      = ('-created_at',)
    readonly_fields = ('business_submitted_at', 'business_verified_at', 'business_verified_by')

    actions = ['verify_business', 'reject_business']

    def verify_business(self, request, queryset):
        updated = queryset.filter(business_status='pending').update(
            business_status='verified',
            business_verified_at=timezone.now(),
            business_verified_by=request.user,
            business_rejection_reason='',
        )
        self.message_user(request, f'{updated} boutique(s) vérifiée(s).', messages.SUCCESS)
    verify_business.short_description = 'Vérifier les boutiques sélectionnées'

    def reject_business(self, request, queryset):
        updated = queryset.filter(business_status='pending').update(
            business_status='rejected',
            business_rejection_reason='Documents non conformes',
        )
        self.message_user(
            request,
            f'{updated} boutique(s) rejetée(s). Éditez pour personnaliser la raison.',
            messages.WARNING,
        )
    reject_business.short_description = 'Rejeter les boutiques sélectionnées'


# ── Enregistre automatiquement tous les autres modèles de l'app users ──
# (BuyerProfile, SupplierProfile, PhoneOTP, …)
# User et BannedPhone déjà enregistrés ci-dessus → skippés via AlreadyRegistered.
for model in apps.get_app_config('users').get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass