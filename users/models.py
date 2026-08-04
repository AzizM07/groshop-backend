from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

# ── Manager ──────────────────────────────────────────────────────
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


# ── User ──────────────────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):

    ROLES = [
        ('buyer',    'Acheteur'),
        ('supplier', 'Fournisseur'),
        ('admin',    'Administrateur'),
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=20, blank=True)
    phone_verified = models.BooleanField(default=False)
    full_name      = models.CharField(max_length=150)
    avatar_url     = models.TextField(blank=True)
    role           = models.CharField(max_length=20, choices=ROLES, default='buyer')
    is_verified    = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    last_seen      = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    @property
    def is_online(self):
        from django.utils import timezone
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).total_seconds() < 120  # 2 min


# ── BuyerProfile ──────────────────────────────────────────────────
class BuyerProfile(models.Model):

    TRADE_TYPES = [
        ('retailer',   'Détaillant'),
        ('wholesaler', 'Grossiste'),
        ('restaurant', 'Restaurant'),
        ('other',      'Autre'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name    = models.CharField(max_length=200, blank=True)
    trade_type      = models.CharField(max_length=30, choices=TRADE_TYPES, blank=True)
    rc_number       = models.CharField(max_length=100, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    wilaya          = models.CharField(max_length=100, blank=True)
    phone_pro       = models.CharField(max_length=20, blank=True)
    total_orders    = models.IntegerField(default=0)
    total_spent_tnd = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'buyer_profiles'

    def __str__(self):
        return f'Acheteur: {self.user.full_name}'


# ── SupplierProfile ───────────────────────────────────────────────
class SupplierProfile(models.Model):

    VERIFICATION_STATUS = [
        ('pending',  'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user                = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name        = models.CharField(max_length=200)
    slug                = models.SlugField(max_length=200, unique=True)
    rc_number           = models.CharField(max_length=100, blank=True)
    tax_number          = models.CharField(max_length=100, blank=True)
    address             = models.TextField(blank=True)
    city                = models.CharField(max_length=100, blank=True)
    wilaya              = models.CharField(max_length=100, blank=True)
    min_order_tnd       = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    verified_at         = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    rating_avg          = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count        = models.IntegerField(default=0)
    followers_count     = models.IntegerField(default=0)
    created_at          = models.DateTimeField(auto_now_add=True)

    # ── Documents de vérification (URLs Supabase) ──
    doc_rne  = models.TextField(blank=True, default='')
    doc_cin  = models.TextField(blank=True, default='')
    doc_rib  = models.TextField(blank=True, default='')
    doc_logo = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'supplier_profiles'

    def __str__(self):
        return f'Fournisseur: {self.company_name}'


# ── SupplierStore ─────────────────────────────────────────────────
class SupplierStore(models.Model):

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier          = models.OneToOneField(SupplierProfile, on_delete=models.CASCADE, related_name='store')

    logo_url          = models.TextField(blank=True)
    banner_url        = models.TextField(blank=True)
    description       = models.TextField(blank=True)
    founded_year      = models.IntegerField(null=True, blank=True)
    certifications    = models.TextField(blank=True)   # CSV "ISO 9001, OEKO-TEX" — le front splitte
    page_views        = models.IntegerField(default=0)
    response_rate     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    response_time_hrs = models.IntegerField(null=True, blank=True)

    # ── Vitrine (contenu éditable par le fournisseur) ──────────────
    #    Tous NOUVEAUX champs → migration purement additive.
    hero_title         = models.TextField(blank=True, default='')
    stats_title        = models.TextField(blank=True, default='')
    stats_description  = models.TextField(blank=True, default='')
    highlight_image_1  = models.TextField(blank=True, default='')
    highlight_image_2  = models.TextField(blank=True, default='')
    about_title_main   = models.CharField(max_length=200, blank=True, default='')
    about_title_accent = models.CharField(max_length=200, blank=True, default='')
    about_image_url    = models.TextField(blank=True, default='')
    about_images       = models.JSONField(default=list, blank=True)   # liste d'URLs
    mission            = models.TextField(blank=True, default='')

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supplier_store'

    def __str__(self):
        return f'Store: {self.supplier.company_name}'


# ══════════════════════════════════════════════════════════════════
# ADDRESS — carnet d'adresses acheteur
# ══════════════════════════════════════════════════════════════════
class Address(models.Model):
    """Adresse de livraison sauvegardée par un acheteur.

    - FK simple vers User (la restriction buyer se fait au niveau permission).
    - is_default garantit une seule adresse par défaut par user (transaction dans la vue).
    - formatted() sert de snapshot texte pour Order.shipping_address.
    """

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')

    # Destinataire
    full_name    = models.CharField(max_length=150)
    phone        = models.CharField(max_length=20)

    # Localisation
    country      = models.CharField(max_length=2, default='TN')   # code ISO
    region       = models.CharField(max_length=100)               # gouvernorat
    city         = models.CharField(max_length=100)
    postal_code  = models.CharField(max_length=20)
    street       = models.CharField(max_length=255)
    additional   = models.CharField(max_length=255, blank=True)   # apt, étage, bâtiment

    is_default   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'addresses'
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f'{self.full_name} — {self.city}, {self.region}'

    def formatted(self):
        """Ligne unique pour affichage / snapshot commande."""
        parts = [self.full_name, self.street]
        if self.additional:
            parts.append(self.additional)
        parts.append(f'{self.city}, {self.region}')
        parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(p for p in parts if p)


# ══════════════════════════════════════════════════════════════════
# BANNEDPHONE — numéros de téléphone bloqués
# ══════════════════════════════════════════════════════════════════
class BannedPhone(models.Model):
    phone     = models.CharField(max_length=20, unique=True)
    reason    = models.CharField(max_length=255, blank=True)
    banned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'banned_phones'

    def __str__(self):
        return self.phone


# ══════════════════════════════════════════════════════════════════
# PHONEOTP — codes de vérification par SMS
# ══════════════════════════════════════════════════════════════════
class PhoneOTP(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_otps')
    phone      = models.CharField(max_length=20)
    code       = models.CharField(max_length=6)
    attempts   = models.PositiveSmallIntegerField(default=0)
    consumed   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'phone_otps'
        indexes = [models.Index(fields=['user', 'phone', 'consumed'])]

    def __str__(self):
        return f'OTP {self.phone} ({"consommé" if self.consumed else "actif"})'