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

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=20, blank=True)
    full_name   = models.CharField(max_length=150)
    avatar_url  = models.TextField(blank=True)
    role        = models.CharField(max_length=20, choices=ROLES, default='buyer')
    is_verified = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    last_seen = models.DateTimeField(null=True, blank=True)
    
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

    class Meta:
        db_table = 'supplier_profiles'

    def __str__(self):
        return f'Fournisseur: {self.company_name}'


# ── SupplierStore ─────────────────────────────────────────────────
class SupplierStore(models.Model):

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier          = models.OneToOneField(SupplierProfile, on_delete=models.CASCADE, related_name='store')

    # ── Visuels ──
    logo_url          = models.TextField(blank=True)
    banner_url        = models.TextField(blank=True)

    # ── Infos publiques ──
    description       = models.TextField(blank=True)
    founded_year      = models.IntegerField(null=True, blank=True)
    certifications    = models.TextField(blank=True)

    # ── Stats ──
    page_views        = models.IntegerField(default=0)
    response_rate     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    response_time_hrs = models.IntegerField(null=True, blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supplier_store'

    def __str__(self):
        return f'Store: {self.supplier.company_name}'