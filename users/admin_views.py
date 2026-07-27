# users/admin_views.py  (NOUVEAU FICHIER)
# Auth de l'espace admin/CEO. Contrairement au login acheteur (qui pose des
# cookies httpOnly), ici on RENVOIE les tokens dans le corps de la réponse,
# car ton client admin les stocke en localStorage et envoie « Authorization: Bearer ».

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate

from .serializers import UserSerializer


class AdminLoginThrottle(ScopedRateThrottle):
    scope = 'login'   # réutilise le throttle 'login' déjà configuré


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AdminLoginThrottle])
def admin_login(request):
    """POST /api/admin/auth/login/  { email, password } → { access, refresh, user }"""
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Email et mot de passe obligatoires.'}, status=400)

    user = authenticate(request, username=email, password=password)
    if not user or not user.is_active:
        return Response({'error': 'Email ou mot de passe incorrect.'}, status=401)

    # ⭐ Gating : seul un compte role='admin' peut entrer dans l'espace CEO
    if user.role != 'admin':
        return Response({'error': 'Accès réservé aux administrateurs.'}, status=403)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user':    UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_logout(request):
    """POST /api/admin/auth/logout/  { refresh } → invalide le refresh token."""
    token = request.data.get('refresh')
    if token:
        try:
            RefreshToken(token).blacklist()   # nécessite token_blacklist installé
        except (TokenError, AttributeError):
            pass
    return Response({'message': 'Déconnecté.'})