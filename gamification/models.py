from django.db import models
import uuid


# ── Coupon ────────────────────────────────────────────────────────
class Coupon(models.Model):

    SOURCES = [
        ('spin_wheel', 'Roue de la fortune'),
        ('promo',      'Promotion admin'),
        ('admin',      'Créé par admin'),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code       = models.CharField(max_length=50, unique=True)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='coupons', null=True, blank=True)
    # null = coupon public pour tout le monde
    amount_tnd = models.DecimalField(max_digits=10, decimal_places=3)
    source     = models.CharField(max_length=20, choices=SOURCES, default='admin')
    is_used    = models.BooleanField(default=False)
    used_at    = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coupons'

    def __str__(self):
        return f'{self.code} → {self.amount_tnd} TND'


# ── SpinPrize ─────────────────────────────────────────────────────
class SpinPrize(models.Model):

    PRIZE_TYPES = [
        ('coupon',        'Coupon réduction'),
        ('free_shipping', 'Livraison gratuite'),
        ('no_prize',      'Pas de chance'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label       = models.CharField(max_length=150)
    prize_type  = models.CharField(max_length=20, choices=PRIZE_TYPES)
    value_tnd   = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    # null si free_shipping ou no_prize
    probability = models.DecimalField(max_digits=5, decimal_places=4)
    # ex: 0.1500 = 15%
    color_hex   = models.CharField(max_length=7, blank=True)
    # ex: #FF4500
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'spin_prizes'

    def __str__(self):
        return f'{self.label} ({self.probability * 100}%)'


# ── UserSpin ──────────────────────────────────────────────────────
class UserSpin(models.Model):

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='spins')
    prize     = models.ForeignKey(SpinPrize, on_delete=models.SET_NULL, null=True, related_name='spins')
    coupon    = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='spin')
    video_ref = models.CharField(max_length=200, unique=True)
    # → ID de la pub AdMob regardée — 1 spin par pub
    spun_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_spins'

    def __str__(self):
        return f'{self.user.full_name} → {self.prize}'