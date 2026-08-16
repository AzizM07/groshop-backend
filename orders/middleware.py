import uuid

GUEST_COOKIE = 'gs_guest_id'
GUEST_MAX_AGE = 60 * 60 * 24 * 365  # 1 an


class GuestCartMiddleware:
    """
    Assure qu'un cookie 'gs_guest_id' existe pour chaque visiteur non
    connecté, pour rattacher son panier. Le cookie survit 1 an, ce qui
    permet de retrouver le panier même après fermeture du navigateur
    (comme AliExpress).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lit le cookie existant, ou en génère un
        guest_id = request.COOKIES.get(GUEST_COOKIE)
        set_cookie = False

        if not guest_id:
            guest_id = str(uuid.uuid4())
            set_cookie = True
        else:
            # Valide le format UUID (sécurité : cookie manipulé)
            try:
                uuid.UUID(guest_id)
            except (ValueError, AttributeError):
                guest_id = str(uuid.uuid4())
                set_cookie = True

        request.guest_id = guest_id
        response = self.get_response(request)

        if set_cookie:
            response.set_cookie(
                GUEST_COOKIE,
                guest_id,
                max_age=GUEST_MAX_AGE,
                httponly=True,
                secure=not __import__('django.conf', fromlist=['settings']).settings.DEBUG,
                samesite='Lax',
            )
        return response