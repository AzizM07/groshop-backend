from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import authenticate
from .serializers import RegisterBuyerSerializer, RegisterSupplierSerializer, UserSerializer, SupplierPublicSerializer
from .models import User, SupplierProfile, SupplierStore
from decouple import config
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')

ACCESS_MAX_AGE  = 15 * 60           # 15 min
REFRESH_MAX_AGE = 7 * 24 * 60 * 60  # 7 jours

REFRESH_PATH = '/api/auth/refresh/'

# ═══════════════════════════════════════════════════════════════════
# COOKIES
# ═══════════════════════════════════════════════════════════════════
# Secure suit DEBUG : False en local (HTTP), True en prod (HTTPS).
COOKIE_SECURE = not settings.DEBUG

# SameSite='Lax' suffit tant que le front (groshop.tn) et l'API (api.groshop.tn)
# partagent le même domaine enregistrable → requêtes same-site.
# Si un jour l'API repasse sur un autre domaine, il faudrait 'None' + Secure.
COOKIE_SAMESITE = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')

# None = cookie host-only (recommandé). Ne définir un domaine que si plusieurs
# sous-domaines doivent partager la session — ça élargit la surface d'attaque.
COOKIE_DOMAIN = getattr(settings, 'AUTH_COOKIE_DOMAIN', None) or None


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return refresh, refresh.access_token


def _set_access_cookie(response, access):
    response.set_cookie(
        key='access_token',
        value=str(access),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=ACCESS_MAX_AGE,
        path='/',
    )


def _set_refresh_cookie(response, refresh):
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=REFRESH_MAX_AGE,
        path=REFRESH_PATH,  # limité à cet endpoint
    )


def set_auth_cookies(response, access, refresh):
    _set_access_cookie(response, access)
    _set_refresh_cookie(response, refresh)


def clear_auth_cookies(response):
    # domain/samesite doivent correspondre à la pose, sinon le cookie survit
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

        response = Response({
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
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

        response = Response({
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
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
        return Response(
            {'error': 'Email et mot de passe obligatoires.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)

    if not user:
        return Response(
            {'error': 'Email ou mot de passe incorrect.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Compte désactivé.'},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh, access = get_tokens_for_user(user)

    response = Response({
        'user': UserSerializer(user).data,
    })
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

    # ── Rotation ──────────────────────────────────────────────────
    user_id = old_refresh.payload.get('user_id')
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        response = Response({'error': 'Session invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
        clear_auth_cookies(response)
        return response

    new_refresh = RefreshToken.for_user(user)

    # Blackliste l'ancien APRÈS avoir émis le nouveau (BLACKLIST_AFTER_ROTATION)
    if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION', False):
        try:
            old_refresh.blacklist()
        except AttributeError:
            # token_blacklist non installé — on ignore silencieusement
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
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, AttributeError):
            pass  # token déjà invalide/expiré — pas grave

    response = Response({'message': 'Déconnecté avec succès.'})
    clear_auth_cookies(response)
    return response


# ── Supplier public (inchangé) ────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_public(request, slug):
    try:
        supplier = SupplierProfile.objects.select_related(
            'user', 'store'
        ).get(slug=slug, verification_status='approved')
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Fournisseur non trouvé.'}, status=404)

    if hasattr(supplier, 'store'):
        SupplierStore.objects.filter(
            supplier=supplier
        ).update(page_views=supplier.store.page_views + 1)

    serializer = SupplierPublicSerializer(supplier)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_products(request, slug):
    try:
        supplier = SupplierProfile.objects.get(slug=slug)
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Fournisseur non trouvé.'}, status=404)

    from products.models import Product
    from products.serializers import ProductListSerializer

    products = Product.objects.filter(
        supplier=supplier,
        status='approved'
    ).prefetch_related('images').order_by('-sold_count')

    category = request.query_params.get('category')
    if category:
        products = products.filter(category__slug=category)

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


# ── Google One Tap ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def google_one_tap(request):
    credential = request.data.get('credential')

    if not credential:
        return Response({'error': 'Credential Google manquant.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        return Response({'error': 'Token Google invalide.'}, status=status.HTTP_401_UNAUTHORIZED)

    email           = idinfo.get('email', '').strip().lower()
    full_name       = idinfo.get('name', '')
    email_verified  = idinfo.get('email_verified', False)

    if not email or not email_verified:
        return Response({'error': 'Email Google non vérifié.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = User.objects.filter(email=email).first()

    if user is None:
        # ── Nouveau compte → buyer par défaut ──
        user = User(
            email=email,
            full_name=full_name or email.split('@')[0],
            role='buyer',
            is_active=True,
            is_verified=True,  # email déjà vérifié par Google
        )
        user.set_unusable_password()
        user.save()

        # Crée le profil acheteur associé si le modèle existe
        try:
            from .models import BuyerProfile
            BuyerProfile.objects.get_or_create(user=user)
        except ImportError:
            pass

    if not user.is_active:
        return Response({'error': 'Compte désactivé.'}, status=status.HTTP_403_FORBIDDEN)

    refresh, access = get_tokens_for_user(user)

    response = Response({
        'user': UserSerializer(user).data,
    })
    set_auth_cookies(response, access, refresh)
    return response


# ── Supplier me ───────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_me(request):
    """
    Retourne le profil fournisseur complet (store, stats, etc.)
    du user connecté. 403 si le user n'est pas un fournisseur.
    """
    if request.user.role != 'supplier':
        return Response({'error': 'Accès réservé aux fournisseurs.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        supplier = SupplierProfile.objects.select_related(
            'user', 'store'
        ).get(user=request.user)
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Profil fournisseur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

    # Réutilise le serializer public, qui contient déjà
    # slug, store info, verification_status, stats, etc.
    serializer = SupplierPublicSerializer(supplier)
    return Response(serializer.data)