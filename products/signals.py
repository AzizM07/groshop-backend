from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Category, ProductVariant, ProductChoiceGroup
from . import search
from .translation_utils import auto_translate_fields, TRANSLATE_CONFIG


def _safe(fn, arg):
    try:
        fn(arg)
    except Exception:
        pass  # Meilisearch indisponible ne doit JAMAIS casser une sauvegarde produit


def _safe_translate(model_cls, pk, fields):
    try:
        auto_translate_fields(model_cls, pk, fields)
    except Exception:
        pass  # AWS Translate indisponible ne doit JAMAIS casser une sauvegarde


@receiver(post_save, sender=Product)
def _index_product(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe(search.index_product, instance))


@receiver(post_delete, sender=Product)
def _unindex_product(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe(search.delete_product, instance.pk))


@receiver(post_save, sender=Product)
def _translate_product(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: _safe_translate(Product, instance.pk, TRANSLATE_CONFIG['Product'])
    )


@receiver(post_save, sender=Category)
def _translate_category(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: _safe_translate(Category, instance.pk, TRANSLATE_CONFIG['Category'])
    )


@receiver(post_save, sender=ProductVariant)
def _translate_variant(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: _safe_translate(ProductVariant, instance.pk, TRANSLATE_CONFIG['ProductVariant'])
    )


@receiver(post_save, sender=ProductChoiceGroup)
def _translate_choice_group(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: _safe_translate(ProductChoiceGroup, instance.pk, TRANSLATE_CONFIG['ProductChoiceGroup'])
    )