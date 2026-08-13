from modeltranslation.translator import register, TranslationOptions
from .models import SubscriptionPlan

@register(SubscriptionPlan)
class SubscriptionPlanTranslationOptions(TranslationOptions):
    fields = ('name',)