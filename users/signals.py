from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupplierStore
from products.translation_utils import auto_translate_fields  # réutilise la fonction générique

STORE_FIELDS = [
    'description',
    'hero_title',
    'stats_title',
    'stats_description',
    'about_title_main',
    'about_title_accent',
    'mission',
]


def _safe_translate(model_cls, pk, fields):
    try:
        auto_translate_fields(model_cls, pk, fields)
    except Exception:
        pass  # AWS Translate indisponible ne doit JAMAIS casser une sauvegarde


@receiver(post_save, sender=SupplierStore)
def _translate_store(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe_translate(SupplierStore, instance.pk, STORE_FIELDS))