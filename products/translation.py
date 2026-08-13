from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product, ProductVariant, ProductChoiceGroup

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'specs_raw')

@register(ProductVariant)
class ProductVariantTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ProductChoiceGroup)
class ProductChoiceGroupTranslationOptions(TranslationOptions):
    fields = ('name',)