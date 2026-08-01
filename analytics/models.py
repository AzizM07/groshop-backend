# analytics/models.py — GROSHOP.tn
from django.db import models
from django.utils import timezone


# ═══════════════════════════════════════════════════════════════
# SESSION  (déclarée AVANT PageView car PageView la référence)
# ═══════════════════════════════════════════════════════════════
class Session(models.Model):
    """Une visite (jusqu'à 30 min d'inactivité). Base du taux de conversion."""

    session_id      = models.CharField(max_length=64, unique=True, db_index=True)
    user            = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='sessions')
    channel         = models.CharField(max_length=30, default='unknown', db_index=True)
    device_type     = models.CharField(max_length=20, default='desktop')
    utm_source      = models.CharField(max_length=100, blank=True)
    utm_campaign    = models.CharField(max_length=100, blank=True)

    started_at      = models.DateTimeField(default=timezone.now, db_index=True)
    last_activity   = models.DateTimeField(default=timezone.now)
    page_view_count = models.PositiveIntegerField(default=1)

    converted       = models.BooleanField(default=False, db_index=True)
    converted_at    = models.DateTimeField(null=True, blank=True)
    order           = models.ForeignKey('orders.Order', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='source_sessions')

    class Meta:
        db_table = 'analytics_session'
        indexes  = [
            models.Index(fields=['channel', 'started_at']),
            models.Index(fields=['converted', 'started_at']),
        ]

    def __str__(self):
        return f"Session {self.session_id[:12]}… [{self.channel}]"


# ═══════════════════════════════════════════════════════════════
# PAGE VIEW
# ═══════════════════════════════════════════════════════════════
class PageView(models.Model):
    """Visite d'une page produit / boutique. POST /api/analytics/pageview/"""

    PAGE_TYPES = [
        ('supplier_shop',  'Boutique fournisseur'),
        ('product_detail', 'Détail produit'),
        ('catalogue',      'Catalogue'),
        ('home',           'Accueil'),
        ('search',         'Recherche'),
    ]
    CHANNELS = [
        ('direct',      'Direct'),
        ('search',      'Recherche organique'),
        ('social',      'Réseaux sociaux'),
        ('email',       'Email'),
        ('referral',    'Référence externe'),
        ('app_ios',     'App iOS'),
        ('app_android', 'App Android'),
        ('unknown',     'Inconnu'),
    ]
    DEVICES = [('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet')]

    supplier   = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE,
                                   related_name='page_views', null=True, blank=True)
    product    = models.ForeignKey('products.Product', on_delete=models.SET_NULL,
                                   related_name='page_views', null=True, blank=True)
    page_type  = models.CharField(max_length=30, choices=PAGE_TYPES, default='product_detail')

    # ⚠️ FIX : vraie FK vers Session (permet session__..., pageviews__...)
    session     = models.ForeignKey(Session, on_delete=models.CASCADE,
                                    related_name='pageviews', null=True, blank=True)
    session_key = models.CharField(max_length=64, db_index=True)

    # ── Identifiant de vue généré côté client (une valeur par ouverture de page) ──
    # Sert à rattacher le "temps passé" (envoyé plus tard, à la sortie de page)
    # à la BONNE ligne de vue, sans dépendre de l'id DB.
    client_view_id = models.CharField(max_length=64, blank=True, db_index=True)

    # Temps passé sur la page, en millisecondes. Rempli a posteriori par le
    # beacon de sortie (POST /api/analytics/duration/). NULL tant qu'inconnu.
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    user       = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='page_views')

    channel      = models.CharField(max_length=30, choices=CHANNELS, default='unknown', db_index=True)
    utm_source   = models.CharField(max_length=100, blank=True)
    utm_medium   = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    referrer     = models.URLField(max_length=500, blank=True)

    device_type = models.CharField(max_length=20, choices=DEVICES, default='desktop')
    user_agent  = models.TextField(blank=True)

    viewed_at   = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'analytics_pageview'
        indexes  = [
            models.Index(fields=['supplier', 'viewed_at']),
            models.Index(fields=['product', 'viewed_at']),
            models.Index(fields=['channel', 'viewed_at']),
        ]

    def __str__(self):
        return f"PageView [{self.page_type}] {self.viewed_at:%Y-%m-%d %H:%M}"


# ═══════════════════════════════════════════════════════════════
# PRODUCT EVENT — interactions sur une fiche produit
# ═══════════════════════════════════════════════════════════════
class ProductEvent(models.Model):
    """Un clic « significatif » sur une fiche produit (ouverture description,
    ajout panier, etc.). POST /api/analytics/product-event/.
    Alimente la colonne « engagement » du dashboard fournisseur."""

    EVENT_TYPES = [
        ('view_description', 'Ouverture description'),
        ('view_image',       'Vue image / galerie'),
        ('select_variant',   'Sélection variante'),
        ('add_to_cart',      'Ajout au panier'),
        ('contact_supplier', 'Contact fournisseur'),
    ]

    supplier    = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE,
                                    related_name='product_events', null=True, blank=True)
    product     = models.ForeignKey('products.Product', on_delete=models.CASCADE,
                                    related_name='events')
    session_key = models.CharField(max_length=64, db_index=True, blank=True)
    user        = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='product_events')

    event_type  = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    created_at  = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'analytics_product_event'
        indexes  = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['product', 'event_type']),
            models.Index(fields=['supplier', 'created_at']),
        ]

    def __str__(self):
        return f"ProductEvent [{self.event_type}] #{self.product_id}"


# ═══════════════════════════════════════════════════════════════
# CANAL D'ACHAT
# ═══════════════════════════════════════════════════════════════
class OrderChannel(models.Model):
    """Enrichit une commande avec son canal d'acquisition (OneToOne, sans toucher Order)."""

    order        = models.OneToOneField('orders.Order', on_delete=models.CASCADE,
                                        related_name='channel_info', primary_key=True)
    channel      = models.CharField(max_length=30, choices=PageView.CHANNELS,
                                    default='unknown', db_index=True)
    session      = models.ForeignKey(Session, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    utm_source   = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    device_type  = models.CharField(max_length=20, default='desktop')

    class Meta:
        db_table = 'analytics_order_channel'

    def __str__(self):
        return f"OrderChannel #{self.order_id} [{self.channel}]"


# ═══════════════════════════════════════════════════════════════
# OBJECTIFS MENSUELS
# ═══════════════════════════════════════════════════════════════
class MonthlyTarget(models.Model):
    """Objectifs mensuels du fournisseur. Unique par (supplier, year, month)."""

    supplier          = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE,
                                          related_name='monthly_targets')
    year              = models.PositiveSmallIntegerField(db_index=True)
    month             = models.PositiveSmallIntegerField(db_index=True)  # 1–12

    revenue_target    = models.DecimalField(max_digits=12, decimal_places=3,
                                            help_text="Objectif de CA en TND")
    orders_target     = models.PositiveIntegerField(default=0)
    new_buyers_target = models.PositiveIntegerField(default=0)
    views_target      = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='created_targets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'analytics_monthly_target'
        unique_together = [('supplier', 'year', 'month')]
        ordering        = ['-year', '-month']
        indexes         = [models.Index(fields=['supplier', 'year', 'month'])]

    def __str__(self):
        return f"Target {self.supplier} {self.year}/{self.month:02d}"

    @property
    def period_label(self):
        import calendar
        return f"{calendar.month_abbr[self.month]} {self.year}"


# ═══════════════════════════════════════════════════════════════
# RÉGION (carte Tunisie)
# ═══════════════════════════════════════════════════════════════
GOUVERNORATS = [
    ('tunis', 'Tunis'), ('ariana', 'Ariana'), ('ben_arous', 'Ben Arous'),
    ('manouba', 'La Manouba'), ('nabeul', 'Nabeul'), ('zaghouan', 'Zaghouan'),
    ('bizerte', 'Bizerte'), ('beja', 'Béja'), ('jendouba', 'Jendouba'),
    ('kef', 'Le Kef'), ('siliana', 'Siliana'), ('kairouan', 'Kairouan'),
    ('kasserine', 'Kassérine'), ('sidi_bouzid', 'Sidi Bouzid'), ('sousse', 'Sousse'),
    ('monastir', 'Monastir'), ('mahdia', 'Mahdia'), ('sfax', 'Sfax'),
    ('gafsa', 'Gafsa'), ('tozeur', 'Tozeur'), ('kebili', 'Kébili'),
    ('gabes', 'Gabès'), ('medenine', 'Médenine'), ('tataouine', 'Tataouine'),
]

# Mapping label affiché → code (utilisé par le parsing d'adresse)
GOUV_LABEL_TO_CODE = {label.lower(): code for code, label in GOUVERNORATS}


class OrderRegion(models.Model):
    """Rattache une commande à un gouvernorat (OneToOne, sans toucher Order)."""

    order       = models.OneToOneField('orders.Order', on_delete=models.CASCADE,
                                       related_name='region_info', primary_key=True)
    gouvernorat = models.CharField(max_length=30, choices=GOUVERNORATS, db_index=True)
    city        = models.CharField(max_length=100, blank=True)
    confidence  = models.FloatField(default=1.0)
    parsed_from = models.TextField(blank=True, help_text="Adresse brute parsée")

    class Meta:
        db_table = 'analytics_order_region'
        indexes  = [models.Index(fields=['gouvernorat'])]

    def __str__(self):
        return f"OrderRegion #{self.order_id} → {self.gouvernorat}"