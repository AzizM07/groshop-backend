from django.contrib import admin, messages
from django.apps import apps
from django.utils import timezone
from .models import Product, Category, ProductVariant, ProductChoiceGroup
from .access_models import SupplierUserUnlock, ProductPriceUnlock
from .translation_utils import auto_translate_fields, TRANSLATE_CONFIG


@admin.action(description="Traduire (AWS Translate)")
def translate_selected(modeladmin, request, queryset):
    fields = TRANSLATE_CONFIG.get(modeladmin.model.__name__)
    if not fields:
        return
    for obj in queryset:
        auto_translate_fields(modeladmin.model, obj.pk, fields)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [translate_selected]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [translate_selected]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    actions = [translate_selected]


@admin.register(ProductChoiceGroup)
class ProductChoiceGroupAdmin(admin.ModelAdmin):
    actions = [translate_selected]


# ══════════════════════════════════════════════════════════════════
#  UNLOCKS — accès prix masqués
# ══════════════════════════════════════════════════════════════════
@admin.register(SupplierUserUnlock)
class SupplierUserUnlockAdmin(admin.ModelAdmin):
    list_display    = ('supplier', 'user', 'granted_at', 'expires_at', 'revoked_at')
    list_filter     = ('granted_at', 'revoked_at')
    search_fields   = ('supplier__company_name', 'user__email', 'user__full_name')
    readonly_fields = ('id', 'granted_at')
    actions         = ['revoke_selected']

    def revoke_selected(self, request, queryset):
        updated = queryset.filter(revoked_at__isnull=True).update(revoked_at=timezone.now())
        self.message_user(request, f'{updated} unlock(s) révoqué(s).', messages.SUCCESS)
    revoke_selected.short_description = 'Révoquer les unlocks sélectionnés'


@admin.register(ProductPriceUnlock)
class ProductPriceUnlockAdmin(admin.ModelAdmin):
    list_display    = ('product', 'user', 'granted_at', 'expires_at', 'revoked_at')
    list_filter     = ('granted_at', 'revoked_at')
    search_fields   = ('product__name', 'user__email', 'user__full_name')
    readonly_fields = ('id', 'granted_at')


# ══════════════════════════════════════════════════════════════════
# Le reste des modèles de l'app garde l'enregistrement générique
# ══════════════════════════════════════════════════════════════════
_already_registered = {
    Product, Category, ProductVariant, ProductChoiceGroup,
    SupplierUserUnlock, ProductPriceUnlock,
}

for model in apps.get_app_config('products').get_models():
    if model in _already_registered:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass