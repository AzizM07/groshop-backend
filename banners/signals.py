from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Banner
from products.translation_utils import auto_translate_fields  # réutilise la fonction générique

BANNER_FIELDS = ['title', 'tag', 'subtitle', 'cta_label']

def _safe_translate(model_cls, pk, fields):
    try:
        auto_translate_fields(model_cls, pk, fields)
    except Exception:
        pass

@receiver(post_save, sender=Banner)
def _translate_banner(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe_translate(Banner, instance.pk, BANNER_FIELDS))