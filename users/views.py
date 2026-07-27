import os
import uuid
from rest_framework.decorators import api_view, permission_classes, throttle_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.text import slugify
from django.db import transaction, IntegrityError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .serializers import (
    RegisterBuyerSerializer, RegisterSupplierSerializer, UserSerializer,
    SupplierPublicSerializer, AddressSerializer,
)
from .models import User, SupplierProfile, SupplierStore, Address
from decouple import config
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')

ACCESS_MAX_AGE  = 15 * 60
REFRESH_MAX_AGE = 7 * 24 * 60 * 60
REFRESH_PATH = '/api/auth/refresh/'

# ═══════════════════════════════════════════════════════════════════
# COOKIES
# ═══════════════════════════════════════════════════════════════════
COOKIE_SECURE   = not settings.DEBUG
COOKIE_SAMESITE = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')
COOKIE_DOMAIN   = getattr(settings, 'AUTH_COOKIE_DOMAIN', None) or None


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return refresh, refresh.access_token


def _set_access_cookie(response, access):
    response.set_cookie(
        key='access_token', value=str(access),
        httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN, max_age=ACCESS_MAX_AGE, path='/',
    )


def _set_refresh_cookie(response, refresh):
    response.set_cookie(
        key='refresh_token', value=str(refresh),
        httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN, max_age=REFRESH_MAX_AGE, path=REFRESH_PATH,
    )


def set_auth_cookies(response, access, refresh):
    _set_access_cookie(response, access)
    _set_refresh_cookie(response, refresh)


def clear_auth_cookies(response):
    response.delete_cookie('access_token', path='/', domain=COOKIE_DOMAIN, samesite=COOKIE_SAMESITE)
    response.delete_cookie('refresh_token', path=REFRESH_PATH, domain=COOKIE_DOMAIN, samesite=COOKIE_SAMESITE)


class LoginThrottle(ScopedRateThrottle):
    scope = 'login'


# ── Register Buyer ───────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register_buyer(request):
    serializer = RegisterBuyerSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh, access = get_tokens_for_user(user)
        response = Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, access, refresh)
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Register Supplier ────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register_supplier(request):
    serializer = RegisterSupplierSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh, access = get_tokens_for_user(user)
        response = Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, access, refresh)
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Login ─────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login(request):
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Email et mot de passe obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)

    if not user:
        return Response({'error': 'Email ou mot de passe incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({'error': 'Compte désactivé.'}, status=status.HTTP_403_FORBIDDEN)

    refresh, access = get_tokens_for_user(user)
    response = Response({'user': UserSerializer(user).data})
    set_auth_cookies(response, access, refresh)
    return response


# ── Refresh ───────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'Refresh token manquant.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        old_refresh = RefreshToken(refresh_token)
    except TokenError:
        return Response({'error': 'Session expirée. Reconnectez-vous.'}, status=status.HTTP_401_UNAUTHORIZED)

    rotate = settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False)

    if not rotate:
        response = Response({'message': 'Token rafraîchi.'})
        _set_access_cookie(response, old_refresh.access_token)
        return response

    user_id = old_refresh.payload.get('user_id')
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        response = Response({'error': 'Session invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
        clear_auth_cookies(response)
        return response

    new_refresh = RefreshToken.for_user(user)

    if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION', False):
        try:
            old_refresh.blacklist()
        except AttributeError:
            pass

    response = Response({'message': 'Token rafraîchi.'})
    _set_access_cookie(response, new_refresh.access_token)
    _set_refresh_cookie(response, new_refresh)
    return response


# ── Me ────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


# ── Logout ────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except (TokenError, AttributeError):
            pass
    response = Response({'message': 'Déconnecté avec succès.'})
    clear_auth_cookies(response)
    return response


# ── Supplier public ───────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_public(request, slug):
    try:
        supplier = SupplierProfile.objects.select_related('user', 'store').get(slug=slug, verification_status='approved')
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Fournisseur non trouvé.'}, status=404)

    if hasattr(supplier, 'store'):
        SupplierStore.objects.filter(supplier=supplier).update(page_views=supplier.store.page_views + 1)

    return Response(SupplierPublicSerializer(supplier).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_products(request, slug):
    try:
        supplier = SupplierProfile.objects.get(slug=slug)
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Fournisseur non trouvé.'}, status=404)

    from products.models import Product
    from products.serializers import ProductListSerializer

    products = Product.objects.filter(supplier=supplier, status='approved').prefetch_related('images').order_by('-sold_count')

    category = request.query_params.get('category')
    if category:
        products = products.filter(category__slug=category)

    return Response(ProductListSerializer(products, many=True).data)


# ═══════════════════════════════════════════════════════════════════
# GOOGLE ONE TAP
# ═══════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([AllowAny])
def google_one_tap(request):
    credential = request.data.get('credential')
    print("🔵 GOOGLE ONE TAP — credential reçu ?", bool(credential))

    if not credential:
        print("🔴 Pas de credential dans la requête")
        return Response({'error': 'Credential Google manquant.'}, status=status.HTTP_400_BAD_REQUEST)

    print("🔵 GOOGLE_CLIENT_ID backend :", repr(GOOGLE_CLIENT_ID))

    try:
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        print("🟢 Token vérifié — audience OK, aud =", idinfo.get('aud'))
    except ValueError as e:
        print("🔴 GOOGLE VERIFY FAILED:", repr(e))
        return Response(
            {'error': 'Token Google invalide.', 'detail': str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print("🔴 GOOGLE UNEXPECTED ERROR:", repr(e))
        return Response(
            {'error': 'Erreur serveur lors de la vérification Google.', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    email          = idinfo.get('email', '').strip().lower()
    full_name      = idinfo.get('name', '')
    email_verified = idinfo.get('email_verified', False)
    print(f"🔵 email={email!r} verified={email_verified}")

    if not email or not email_verified:
        print("🔴 Email absent ou non vérifié")
        return Response({'error': 'Email Google non vérifié.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = User.objects.filter(email=email).first()

    if user is None:
        print("🔵 Création d'un nouveau compte buyer pour", email)
        user = User(
            email=email,
            full_name=full_name or email.split('@')[0],
            role='buyer',
            is_active=True,
            is_verified=True,
        )
        user.set_unusable_password()
        user.save()

        try:
            from .models import BuyerProfile
            BuyerProfile.objects.get_or_create(user=user)
        except ImportError:
            pass
        except Exception as e:
            print("🟡 BuyerProfile non créé:", repr(e))
    else:
        print("🔵 Compte existant trouvé, id =", user.id, "role =", user.role)

    if not user.is_active:
        print("🔴 Compte désactivé")
        return Response({'error': 'Compte désactivé.'}, status=status.HTTP_403_FORBIDDEN)

    refresh, access = get_tokens_for_user(user)
    print("🟢 Connexion Google réussie, cookies posés pour", email)

    response = Response({'user': UserSerializer(user).data})
    set_auth_cookies(response, access, refresh)
    return response


# ── Supplier me ───────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_me(request):
    if request.user.role != 'supplier':
        return Response({'error': 'Accès réservé aux fournisseurs.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        supplier = SupplierProfile.objects.select_related('user', 'store').get(user=request.user)
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Profil fournisseur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(SupplierPublicSerializer(supplier).data)


# ══════════════════════════════════════════════════════════════════
#  INSCRIPTION FOURNISSEUR
# ══════════════════════════════════════════════════════════════════
class SignupThrottle(ScopedRateThrottle):
    scope = 'login'


def _unique_supplier_slug(base):
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
                slug=_unique_supplier_slug(company_name),
                tax_number=(d.get('tax_number') or '').strip(),
                rc_number=(d.get('rc_number') or '').strip(),
                address=(d.get('address') or '').strip(),
                city=(d.get('city') or '').strip(),
                wilaya=(d.get('wilaya') or '').strip(),
                doc_rne=d.get('doc_rne', ''),
                doc_cin=d.get('doc_cin', ''),
                doc_rib=d.get('doc_rib', ''),
                doc_logo=d.get('doc_logo', ''),
                verification_status='pending',
            )
    except IntegrityError:
        return Response({'error': 'Conflit lors de la création du compte.'}, status=409)

    return Response(
        {'message': 'Compte fournisseur créé. En attente de validation par un administrateur.'},
        status=201,
    )


# ── Upload document ───────────────────────────────────────────────
ALLOWED_DOC_EXT = {'.pdf', '.jpg', '.jpeg', '.png', '.svg'}
ALLOWED_DOC_CONTENT_TYPES = {
    'application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml',
}
MAX_DOC_SIZE_MB = 5


class DocUploadThrottle(ScopedRateThrottle):
    scope = 'login'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([DocUploadThrottle])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    f = request.FILES.get('file')
    if not f:
        return Response({'error': 'Aucun fichier.'}, status=400)

    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ALLOWED_DOC_EXT or f.content_type not in ALLOWED_DOC_CONTENT_TYPES:
        return Response({'error': 'Format non supporté (pdf, png, jpg, jpeg, svg).'}, status=400)
    if f.size > MAX_DOC_SIZE_MB * 1024 * 1024:
        return Response({'error': f'Fichier trop volumineux (max {MAX_DOC_SIZE_MB} Mo).'}, status=400)

    key  = f"suppliers/{uuid.uuid4().hex}{ext}"
    path = default_storage.save(key, ContentFile(f.read()))
    url  = default_storage.url(path)
    if url.startswith('/'):
        url = request.build_absolute_uri(url)
    return Response({'url': url}, status=201)


# ══════════════════════════════════════════════════════════════════
# ADDRESS — CRUD carnet d'adresses buyer
# ══════════════════════════════════════════════════════════════════
def _ensure_buyer(user):
    """Retourne une Response 403 si user n'est pas buyer, sinon None."""
    if user.role != 'buyer':
        return Response({'error': 'Accès réservé aux acheteurs.'}, status=status.HTTP_403_FORBIDDEN)
    return None


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def addresses_list(request):
    """
    GET  /api/users/addresses/  → liste des adresses du buyer
    POST /api/users/addresses/  → créer une adresse
    """
    err = _ensure_buyer(request.user)
    if err:
        return err

    if request.method == 'GET':
        qs = Address.objects.filter(user=request.user)
        return Response(AddressSerializer(qs, many=True).data)

    # POST
    ser = AddressSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    with transaction.atomic():
        # Première adresse → force default. Sinon respecte is_default demandé.
        is_first    = not Address.objects.filter(user=request.user).exists()
        wants_default = ser.validated_data.get('is_default', False)
        will_default  = is_first or wants_default

        if will_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        # save avec l'user et le flag final
        ser.validated_data['is_default'] = will_default
        addr = ser.save(user=request.user)

    return Response(AddressSerializer(addr).data, status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def address_detail(request, pk):
    """
    GET    /api/users/addresses/<id>/
    PATCH  /api/users/addresses/<id>/
    DELETE /api/users/addresses/<id>/
    """
    err = _ensure_buyer(request.user)
    if err:
        return err

    try:
        addr = Address.objects.get(id=pk, user=request.user)
    except Address.DoesNotExist:
        return Response({'error': 'Adresse non trouvée.'}, status=404)

    if request.method == 'GET':
        return Response(AddressSerializer(addr).data)

    if request.method == 'DELETE':
        was_default = addr.is_default
        addr.delete()
        # Si on supprime la default → promouvoir la plus récente restante
        if was_default:
            next_addr = Address.objects.filter(user=request.user).first()
            if next_addr:
                next_addr.is_default = True
                next_addr.save(update_fields=['is_default'])
        return Response(status=204)

    # PATCH
    ser = AddressSerializer(addr, data=request.data, partial=True)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    with transaction.atomic():
        new_default = ser.validated_data.get('is_default', addr.is_default)
        if new_default and not addr.is_default:
            Address.objects.filter(user=request.user, is_default=True) \
                           .exclude(id=addr.id) \
                           .update(is_default=False)
        ser.save()

    return Response(AddressSerializer(addr).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def address_set_default(request, pk):
    """
    POST /api/users/addresses/<id>/default/
    Marque cette adresse comme par défaut, retire le flag des autres.
    """
    err = _ensure_buyer(request.user)
    if err:
        return err

    try:
        addr = Address.objects.get(id=pk, user=request.user)
    except Address.DoesNotExist:
        return Response({'error': 'Adresse non trouvée.'}, status=404)

    with transaction.atomic():
        Address.objects.filter(user=request.user, is_default=True) \
                       .exclude(id=addr.id) \
                       .update(is_default=False)
        addr.is_default = True
        addr.save(update_fields=['is_default'])

    return Response(AddressSerializer(addr).data)