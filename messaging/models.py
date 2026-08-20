# messaging/models.py — GROSHOP.tn
from django.db import models
import uuid
from users.models import User, SupplierProfile
from products.models import Product


class Conversation(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_buyer')
    supplier    = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='conversations')
    product     = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    last_msg_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-last_msg_at']
        constraints = [
            models.UniqueConstraint(
                fields=['buyer', 'supplier', 'product'],
                name='unique_conversation'
            )
        ]
        indexes = [
            models.Index(fields=['buyer', 'last_msg_at']),
            models.Index(fields=['supplier', 'last_msg_at']),
        ]

    def __str__(self):
        return f'{self.buyer.full_name} ↔ {self.supplier.company_name}'


class Message(models.Model):

    MESSAGE_TYPES = [
        ('text',           'Texte'),
        ('quote_request',  'Demande de devis'),   # envoyé par l'acheteur à la soumission de la popup perso
        ('quote_response', 'Réponse de devis'),   # envoyé par le fournisseur avec le prix
        ('quote_accepted', 'Devis accepté'),      # message système à l'acceptation
        ('quote_rejected', 'Devis refusé'),       # message système au refus
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation   = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content        = models.TextField()
    attachment_url = models.TextField(blank=True)
    is_read        = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    # ── Type de message + lien devis ──
    message_type          = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    customization_request = models.ForeignKey(
        'orders.CustomizationRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        help_text="Uniquement pour les messages liés à un devis de personnalisation",
    )

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['conversation', 'is_read']),
        ]

    def __str__(self):
        return f'Message de {self.sender.full_name}'