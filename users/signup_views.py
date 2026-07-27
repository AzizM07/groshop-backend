# users/signup_views.py  (NOUVEAU FICHIER)
# Inscription fournisseur → crée un User(role='supplier') + un SupplierProfile
# en statut 'pending', qui apparaît ensuite dans l'admin (onglet Fournisseurs)
# pour validation. Remplace l'ancien flux Supabase.

from django.utils.text import slugify
from django.db import transaction, IntegrityError

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import User, SupplierProfile


class SignupThrottle(ScopedRateThrottle):
    scope = 'login'   # réutilise le throttle 'login' déjà configuré (5/min)


def _unique_slug(base):
    base = slugify(base) or 'fournisseur'
    slug, i = base, 1
    while SupplierProfile.objects.filter(slug=slug).exists():
        i += 1
        slug = f'{base}-{i}'
    return slug


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SignupThrottle])
def supplier_signup(request):
    """POST /api/auth/supplier-signup/
    body: { email, password, full_name, company_name, tax_number?, rc_number?,
            address?, city?, wilaya?, phone? }
    """
    d = request.data
    email        = (d.get('email') or '').strip().lower()
    password     = d.get('password') or ''
    full_name    = (d.get('full_name') or '').strip()
    company_name = (d.get('company_name') or '').strip()

    if not (email and password and full_name and company_name):
        return Response({'error': 'Champs obligatoires manquants.'}, status=400)
    if len(password) < 6:
        return Response({'error': 'Mot de passe : 6 caractères minimum.'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Un compte existe déjà avec cet email.'}, status=409)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                phone=(d.get('phone') or '').strip(),
                role='supplier',
            )
            SupplierProfile.objects.create(
                user=user,
                company_name=company_name,
                slug=_unique_slug(company_name),
                tax_number=(d.get('tax_number') or '').strip(),   # matricule fiscal
                rc_number=(d.get('rc_number') or '').strip(),
                address=(d.get('address') or '').strip(),
                city=(d.get('city') or '').strip(),
                wilaya=(d.get('wilaya') or '').strip(),
                verification_status='pending',
            )
    except IntegrityError:
        return Response({'error': 'Conflit lors de la création du compte.'}, status=409)

    return Response(
        {'message': 'Compte fournisseur créé. En attente de validation par un administrateur.'},
        status=201,
    )