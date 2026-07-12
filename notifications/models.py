from django.db import models
import uuid
from users.models import User


# ── Notification ──────────────────────────────────────────────────
class Notification(models.Model):

    TYPES = [
        ('new_order',        'Nouvelle commande'),
        ('order_status',     'Statut commande mis à jour'),
        ('message',          'Nouveau message'),
        ('promo',            'Promotion'),
        ('product_approved', 'Produit approuvé'),
        ('product_rejected', 'Produit rejeté'),
        ('new_review',       'Nouvel avis'),
        ('spin_reward',      'Récompense roue'),
    ]

    CHANNELS = [
        ('push',   'Notification push'),
        ('in_app', 'In-app'),
        ('email',  'Email'),
    ]

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type      = models.CharField(max_length=50, choices=TYPES)
    title     = models.CharField(max_length=200)
    body      = models.TextField()
    data      = models.JSONField(default=dict, blank=True)
    channel   = models.CharField(max_length=20, choices=CHANNELS, default='in_app')
    is_read   = models.BooleanField(default=False)
    sent_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-sent_at']
        indexes  = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.type} → {self.user.full_name}'