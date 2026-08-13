from modeltranslation.translator import register, TranslationOptions
from .models import PushNotification


@register(PushNotification)
class PushNotificationTranslationOptions(TranslationOptions):

    fields = ('title', 'body')