from django.contrib import admin
from django.apps import apps
from .models import Product, Category, ProductVariant, ProductChoiceGroup
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


# Le reste des modèles de l'app garde l'enregistrement générique existant
_already_registered = {Product, Category, ProductVariant, ProductChoiceGroup}

for model in apps.get_app_config('products').get_models():
    if model in _already_registered:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass