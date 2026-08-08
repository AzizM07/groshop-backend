from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # ⭐ Sans cette ligne, orders/signals.py n'est jamais importé,
        # donc post_save sur SubOrder ne déclenche RIEN, et le statut
        # de la commande côté buyer ne se met jamais à jour tout seul.
        import orders.signals  # noqa: F401