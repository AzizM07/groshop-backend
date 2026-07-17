# users/authentication.py — GROSHOP.tn
# Lit le JWT depuis un cookie httpOnly au lieu du header Authorization.

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Ordre de lecture : cookie `access_token`, puis header Authorization
    (utile pour l'app mobile / Postman / les tests).

    Un token expiré ou invalide renvoie None au lieu de lever une exception :
    la requête devient anonyme et les vues AllowAny continuent de répondre 200.
    Les vues IsAuthenticated renverront 401, ce qui déclenche le refresh côté front.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')

        if not raw_token:
            # Fallback header Authorization: Bearer <token>
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            # Token expiré / signature invalide / user supprimé → anonyme
            return None