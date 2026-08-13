from modeltranslation.translator import register, TranslationOptions
from .models import SupplierStore


@register(SupplierStore)
class SupplierStoreTranslationOptions(TranslationOptions):
    # Champs vitrine visibles publiquement sur la page boutique.
    # `certifications` (CSV type "ISO 9001, OEKO-TEX") est volontairement
    # exclu : ce sont des labels standards internationaux, les traduire
    # casserait leur reconnaissance.
    fields = (
        'description',
        'hero_title',
        'stats_title',
        'stats_description',
        'about_title_main',
        'about_title_accent',
        'mission',
    )