from modeltranslation.translator import register, TranslationOptions
from .models import Banner

@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'tag', 'subtitle', 'cta_label')