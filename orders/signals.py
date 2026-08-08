from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, SubOrder

SUBORDER_PROGRESS = ['pending', 'confirmed', 'in_production', 'shipped', 'delivered']


def _order_status_from_suborder_statuses(statuses):
    if not statuses:
        return None
    non_cancelled = [s for s in statuses if s != 'cancelled']
    if not non_cancelled:
        return 'cancelled'
    # La commande globale reflète le sous-statut le "moins avancé"
    # tant que tous les fournisseurs n'ont pas atteint le même stade.
    return min(non_cancelled, key=lambda s: SUBORDER_PROGRESS.index(s))


@receiver(post_save, sender=SubOrder)
def sync_order_status_from_suborders(sender, instance, **kwargs):
    order = instance.order
    statuses = list(order.sub_orders.values_list('status', flat=True))
    new_status = _order_status_from_suborder_statuses(statuses)
    if new_status and order.status != new_status:
        # ⭐ CORRIGÉ : on force updated_at nous-mêmes, car .update()
        # ne déclenche pas auto_now. Sans ça, le front (qui trie/affiche
        # parfois par updated_at) peut sembler ne pas avoir changé.
        Order.objects.filter(id=order.id).update(
            status=new_status,
            updated_at=timezone.now(),
        )