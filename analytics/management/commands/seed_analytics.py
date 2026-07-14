# analytics/management/commands/seed_analytics.py — GROSHOP.tn
"""
Génère des données réalistes pour visualiser le dashboard fournisseur.

    python manage.py seed_analytics --supplier sfax-textile-co --days 60 --orders 45
    python manage.py seed_analytics --clear          # supprime UNIQUEMENT les données seedées
    python manage.py seed_analytics --days 90 --orders 80 --views 1500

⚠️  Écrit dans la base pointée par DATABASE_URL (.env). Si c'est Neon, ce sont
    de vraies données de prod. Utiliser --clear pour tout retirer.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from analytics.models import PageView, Session, OrderChannel, OrderRegion, GOUVERNORATS
from orders.models import Order, SubOrder, OrderItem
from products.models import Product
from users.models import SupplierProfile

User = get_user_model()

# Marqueur : permet à --clear de ne supprimer QUE ce qui a été seedé
SEED_TAG   = '[seed]'
SEED_EMAIL = 'seed.buyer'

CHANNELS = [
    ('direct', 30), ('search', 28), ('social', 18),
    ('referral', 10), ('app_android', 8), ('email', 4), ('app_ios', 2),
]
DEVICES   = [('mobile', 62), ('desktop', 30), ('tablet', 8)]
PAGES     = [('product_detail', 55), ('catalogue', 20), ('supplier_shop', 12), ('search', 8), ('home', 5)]
PAYMENTS  = [('cod', 55), ('d17', 18), ('flouci', 14), ('virement', 8), ('sobflous', 5)]
STATUSES  = [('delivered', 45), ('shipped', 16), ('in_production', 12),
             ('confirmed', 12), ('pending', 10), ('cancelled', 5)]

# Gouvernorats pondérés (Tunis/Sfax/Sousse concentrent le gros)
GOUV_WEIGHTS = [
    ('tunis', 24), ('sfax', 17), ('sousse', 13), ('ariana', 10), ('nabeul', 8),
    ('monastir', 7), ('bizerte', 5), ('gabes', 4), ('kairouan', 4), ('ben_arous', 3),
    ('medenine', 2), ('gafsa', 2), ('beja', 1),
]
GOUV_CITY = {
    'tunis': 'Tunis', 'sfax': 'Sfax', 'sousse': 'Sousse', 'ariana': 'Ariana',
    'nabeul': 'Nabeul', 'monastir': 'Monastir', 'bizerte': 'Bizerte', 'gabes': 'Gabès',
    'kairouan': 'Kairouan', 'ben_arous': 'Ben Arous', 'medenine': 'Djerba',
    'gafsa': 'Gafsa', 'beja': 'Béja',
}
FIRST = ['Amel', 'Karim', 'Sonia', 'Nabil', 'Leila', 'Mehdi', 'Rania', 'Omar',
         'Ines', 'Sami', 'Nour', 'Hedi', 'Salma', 'Ayoub', 'Dorra']
LAST  = ['Ben Salem', 'Trabelsi', 'Mansour', 'Hamdi', 'Fekih', 'Louhichi',
         'Chaker', 'Guiga', 'Jebali', 'Sassi', 'Bouazizi', 'Ayari']


def weighted(pairs):
    vals, w = zip(*pairs)
    return random.choices(vals, weights=w, k=1)[0]


def rand_dt(days_back):
    """Date aléatoire dans les N derniers jours, biaisée vers le récent + heures de bureau."""
    now = timezone.now()
    d   = int(random.triangular(0, days_back, days_back * 0.35))
    return now - timedelta(days=d, hours=random.randint(0, 23), minutes=random.randint(0, 59))


class Command(BaseCommand):
    help = "Seed des commandes + analytics pour visualiser le dashboard fournisseur."

    def add_arguments(self, p):
        p.add_argument('--supplier', type=str, default=None, help="slug du fournisseur (défaut : tous)")
        p.add_argument('--days',   type=int, default=60,   help="profondeur historique (défaut 60)")
        p.add_argument('--orders', type=int, default=45,   help="commandes par fournisseur (défaut 45)")
        p.add_argument('--views',  type=int, default=900,  help="pages vues par fournisseur (défaut 900)")
        p.add_argument('--clear',  action='store_true',    help="supprime les données seedées puis quitte")
        p.add_argument('--yes',    action='store_true',    help="ne pas demander confirmation")

    # ──────────────────────────────────────────────────────────────
    def handle(self, *args, **o):
        from django.conf import settings
        db = settings.DATABASES['default']
        host = db.get('HOST', '?')
        self.stdout.write(self.style.WARNING(f"→ Base cible : {db.get('NAME')} @ {host}"))
        if 'neon' in str(host).lower():
            self.stdout.write(self.style.ERROR("⚠️  C'est ta base NEON (production)."))

        if o['clear']:
            return self.clear(o['yes'])

        if not o['yes']:
            if input("Continuer ? (oui/non) ").strip().lower() not in ('oui', 'o', 'yes', 'y'):
                raise CommandError("Annulé.")

        suppliers = (SupplierProfile.objects.filter(slug=o['supplier'])
                     if o['supplier'] else SupplierProfile.objects.all())
        if not suppliers.exists():
            raise CommandError("Aucun fournisseur trouvé.")

        buyers = self.get_buyers(12)

        for sup in suppliers:
            prods = list(Product.objects.filter(supplier=sup, status='approved').prefetch_related('price_tiers'))
            if not prods:
                prods = list(Product.objects.filter(supplier=sup).prefetch_related('price_tiers'))
            if not prods:
                self.stdout.write(self.style.WARNING(f"  ↷ {sup.company_name} : aucun produit, ignoré."))
                continue

            self.stdout.write(f"\n▸ {sup.company_name} ({len(prods)} produits)")
            sessions = self.seed_traffic(sup, prods, o['views'], o['days'])
            self.seed_orders(sup, prods, buyers, sessions, o['orders'], o['days'])

        self.stdout.write(self.style.SUCCESS("\n✓ Terminé. Recharge le dashboard."))

    # ──────────────────────────────────────────────────────────────
    def get_buyers(self, n):
        """Acheteurs seedés — réutilisés s'ils existent déjà."""
        buyers = list(User.objects.filter(email__startswith=SEED_EMAIL))
        if len(buyers) >= n:
            return buyers[:n]

        for i in range(len(buyers), n):
            email = f"{SEED_EMAIL}{i}@groshop.test"
            name  = f"{random.choice(FIRST)} {random.choice(LAST)}"
            try:
                u = User.objects.create_user(email=email, password='seedpass123', full_name=name)
            except TypeError:
                u = User(email=email, full_name=name)
                u.set_password('seedpass123')
                u.save()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Création acheteur impossible : {e}"))
                break
            buyers.append(u)

        if not buyers:
            buyers = list(User.objects.all()[:n])
        if not buyers:
            raise CommandError("Aucun acheteur disponible.")
        return buyers

    # ── Trafic : sessions + pages vues ────────────────────────────
    def seed_traffic(self, sup, prods, n_views, days):
        n_sessions = max(n_views // 4, 10)
        sessions, pvs = [], []

        for i in range(n_sessions):
            started = rand_dt(days)
            ch, dev = weighted(CHANNELS), weighted(DEVICES)
            sid     = f"seed-{sup.id.hex[:6]}-{i}-{random.randint(1000, 9999)}"
            n_pages = random.randint(1, 6)
            sessions.append(Session(
                session_id=sid, channel=ch, device_type=dev,
                started_at=started,
                last_activity=started + timedelta(minutes=random.randint(1, 25)),
                page_view_count=n_pages,
            ))
            for _ in range(n_pages):
                ptype = weighted(PAGES)
                pvs.append(dict(
                    supplier=sup,
                    product=random.choice(prods) if ptype == 'product_detail' else None,
                    page_type=ptype, session_key=sid, channel=ch, device_type=dev,
                    viewed_at=started + timedelta(minutes=random.randint(0, 25)),
                ))

        with transaction.atomic():
            Session.objects.bulk_create(sessions, batch_size=500)
            smap = {s.session_id: s for s in Session.objects.filter(
                session_id__in=[s.session_id for s in sessions])}
            PageView.objects.bulk_create(
                [PageView(session=smap.get(p['session_key']), **p) for p in pvs],
                batch_size=500,
            )

        self.stdout.write(f"  · {len(sessions)} sessions, {len(pvs)} pages vues")
        return list(smap.values())

    # ── Commandes ─────────────────────────────────────────────────
    def seed_orders(self, sup, prods, buyers, sessions, n_orders, days):
        made = 0
        for _ in range(n_orders):
            created = rand_dt(days)
            gouv    = weighted(GOUV_WEIGHTS)
            city    = GOUV_CITY.get(gouv, '')
            buyer   = random.choice(buyers)
            picked  = random.sample(prods, k=min(random.randint(1, 3), len(prods)))

            with transaction.atomic():
                order = Order.objects.create(
                    buyer=buyer,
                    shipping_address=f"{random.randint(1, 180)} rue de la République, {city}, {dict(GOUVERNORATS)[gouv]}",
                    payment_method=weighted(PAYMENTS),
                    payment_status=random.choice(['paid', 'paid', 'unpaid']),
                    status='pending',
                    notes=SEED_TAG,
                )
                # created_at est auto_now_add → on force après coup
                Order.objects.filter(id=order.id).update(created_at=created)

                sub_status = weighted(STATUSES)
                sub = SubOrder.objects.create(
                    order=order, supplier=sup, status=sub_status, subtotal_tnd=Decimal('0'),
                )
                SubOrder.objects.filter(id=sub.id).update(created_at=created)

                subtotal = Decimal('0')
                for p in picked:
                    qty  = max(p.moq, 1) * random.randint(1, 4)
                    tier = p.price_tiers.filter(min_qty__lte=qty).order_by('-min_qty').first()
                    unit = tier.price_tnd if tier else p.base_price_tnd
                    tot  = Decimal(unit) * qty
                    OrderItem.objects.create(
                        sub_order=sub, product=p, quantity=qty,
                        unit_price_tnd=unit, total_tnd=tot,
                    )
                    subtotal += tot

                SubOrder.objects.filter(id=sub.id).update(subtotal_tnd=subtotal)
                Order.objects.filter(id=order.id).update(total_tnd=subtotal)

                # ── Attribution : canal + région + session convertie ──
                sess = random.choice(sessions) if sessions and random.random() < 0.75 else None
                OrderChannel.objects.create(
                    order=order,
                    channel=sess.channel if sess else weighted(CHANNELS),
                    session=sess,
                    device_type=sess.device_type if sess else weighted(DEVICES),
                )
                OrderRegion.objects.create(
                    order=order, gouvernorat=gouv, city=city,
                    confidence=1.0, parsed_from=order.shipping_address,
                )
                if sess and not sess.converted:
                    sess.converted    = True
                    sess.converted_at = created
                    sess.order        = order
                    sess.save(update_fields=['converted', 'converted_at', 'order'])
                made += 1

        self.stdout.write(f"  · {made} commandes créées")

    # ── Nettoyage ─────────────────────────────────────────────────
    def clear(self, skip_confirm):
        if not skip_confirm:
            if input("Supprimer TOUTES les données seedées ? (oui/non) ").strip().lower() not in ('oui', 'o', 'yes', 'y'):
                raise CommandError("Annulé.")

        orders = Order.objects.filter(notes=SEED_TAG)
        n_ord  = orders.count()
        orders.delete()                                     # cascade : SubOrder, OrderItem, Channel, Region

        n_pv = PageView.objects.filter(session_key__startswith='seed-').delete()[0]
        n_se = Session.objects.filter(session_id__startswith='seed-').delete()[0]
        n_us = User.objects.filter(email__startswith=SEED_EMAIL).delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f"✓ Supprimé : {n_ord} commandes, {n_pv} pages vues, {n_se} sessions, {n_us} acheteurs."
        ))