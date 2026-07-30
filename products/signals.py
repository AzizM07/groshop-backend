from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from . import search

def _safe(fn, arg):
    try:
        fn(arg)
    except Exception:
        pass  # Meilisearch indisponible ne doit JAMAIS casser une sauvegarde produit

@receiver(post_save, sender=Product)
def _index_product(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe(search.index_product, instance))

@receiver(post_delete, sender=Product)
def _unindex_product(sender, instance, **kwargs):
    transaction.on_commit(lambda: _safe(search.delete_product, instance.pk))