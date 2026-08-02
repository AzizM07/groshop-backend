# users/social_auth.py — GROSHOP.tn
# Connexion sociale (Google / Facebook / LinkedIn) en flow "redirection serveur".
#
# Principe (identique pour les 3) :
#   1. Le bouton front envoie l'utilisateur vers  /api/auth/<provider>/start/
#   2. On le redirige vers le provider (Google/Facebook/LinkedIn) pour qu'il autorise.
#   3. Le provider le renvoie vers  /api/auth/<provider>/callback/  avec un "code".
#   4. On échange ce code contre un access_token, on récupère email + nom,
#      on crée/retrouve le User, on pose TES cookies JWT, et on redirige vers le front.
#
# Aucune session Django n'est utilisée pour l'auth : on réutilise exactement
# tes helpers cookies (set_auth_cookies / get_tokens_for_user) de views.py.
# La session ne sert qu'à stocker le "state" anti-CSRF le temps de l'aller-retour.

import secrets
import urllib.parse
import requests as http

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from decouple import config

from .models import User
# On réutilise TES helpers existants (définis dans users/views.py)
from .views import set_auth_cookies, get_tokens_for_user


# ── URLs publiques ────────────────────────────────────────────────
# En dev  : FRONTEND_URL=http://localhost:5173   API_PUBLIC_URL=http://localhost:8000
# En prod : FRONTEND_URL=https://groshop.tn      API_PUBLIC_URL=https://api.groshop.tn
FRONTEND_URL   = config('FRONTEND_URL',   default='http://localhost:5173')
API_PUBLIC_URL = config('API_PUBLIC_URL', default='http://localhost:8000')


def _redirect_uri(provider):
    # Doit correspondre EXACTEMENT à l'URL enregistrée dans la console du provider
    return f'{API_PUBLIC_URL}/api/auth/{provider}/callback/'


# ── Config des providers ──────────────────────────────────────────
# default='' partout : le module s'importe même si tu n'as pas encore mis
# les clés dans .env (on vérifie leur présence au moment de l'appel).
PROVIDERS = {
    'google': {
        'authorize':     'https://accounts.google.com/o/oauth2/v2/auth',
        'token':         'https://oauth2.googleapis.com/token',
        'userinfo':      'https://openidconnect.googleapis.com/v1/userinfo',
        'scope':         'openid email profile',
        'client_id':     config('GOOGLE_CLIENT_ID',     default=''),
        'client_secret': config('GOOGLE_CLIENT_SECRET', default=''),
        'extra_auth':    {'access_type': 'online', 'prompt': 'select_account'},
    },
    'facebook': {
        'authorize':     'https://www.facebook.com/v19.0/dialog/oauth',
        'token':         'https://graph.facebook.com/v19.0/oauth/access_token',
        'userinfo':      'https://graph.facebook.com/me?fields=id,name,email',
        'scope':         'email public_profile',
        'client_id':     config('FACEBOOK_APP_ID',     default=''),
        'client_secret': config('FACEBOOK_APP_SECRET', default=''),
        'extra_auth':    {},
    },
    'linkedin': {
        'authorize':     'https://www.linkedin.com/oauth/v2/authorization',
        'token':         'https://www.linkedin.com/oauth/v2/accessToken',
        'userinfo':      'https://api.linkedin.com/v2/userinfo',
        'scope':         'openid profile email',
        'client_id':     config('LINKEDIN_CLIENT_ID',     default=''),
        'client_secret': config('LINKEDIN_CLIENT_SECRET', default=''),
        'extra_auth':    {},
    },
}


def _fail(provider, reason):
    """Redirige vers le front avec un code d'erreur lisible dans l'URL."""
    return HttpResponseRedirect(f'{FRONTEND_URL}/login?social={provider}_{reason}')


def _get_or_create_social_user(email, full_name):
    """
    Retrouve le compte par email, sinon en crée un (buyer, sans mot de passe).
    Même logique que ton google_one_tap.
    """
    user = User.objects.filter(email=email).first()
    if user is None:
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
        except Exception:
            pass
    return user


# ── 1) Démarrage : redirige vers le provider ──────────────────────
@require_GET
def social_start(request, provider):
    cfg = PROVIDERS.get(provider)
    if not cfg:
        return HttpResponseBadRequest('Provider inconnu.')
    if not cfg['client_id'] or not cfg['client_secret']:
        return _fail(provider, 'notconfigured')

    state = secrets.token_urlsafe(24)
    request.session[f'oauth_state_{provider}'] = state

    params = {
        'response_type': 'code',
        'client_id':     cfg['client_id'],
        'redirect_uri':  _redirect_uri(provider),
        'scope':         cfg['scope'],
        'state':         state,
        **cfg['extra_auth'],
    }
    return HttpResponseRedirect(cfg['authorize'] + '?' + urllib.parse.urlencode(params))


# ── 2) Retour : le provider nous renvoie ici avec ?code=... ───────
@require_GET
def social_callback(request, provider):
    cfg = PROVIDERS.get(provider)
    if not cfg:
        return HttpResponseBadRequest('Provider inconnu.')

    if request.GET.get('error'):
        return _fail(provider, 'denied')

    code     = request.GET.get('code')
    state    = request.GET.get('state')
    expected = request.session.pop(f'oauth_state_{provider}', None)
    if not code or not state or state != expected:
        return _fail(provider, 'state')

    # a) échange code -> access_token
    try:
        token_res = http.post(
            cfg['token'],
            data={
                'grant_type':    'authorization_code',
                'code':          code,
                'redirect_uri':  _redirect_uri(provider),
                'client_id':     cfg['client_id'],
                'client_secret': cfg['client_secret'],
            },
            headers={'Accept': 'application/json'},
            timeout=10,
        ).json()
    except Exception:
        return _fail(provider, 'token')

    access_token = token_res.get('access_token')
    if not access_token:
        return _fail(provider, 'token')

    # b) récupère le profil (email + nom) — Bearer marche pour les 3
    try:
        ui = http.get(
            cfg['userinfo'],
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        ).json()
    except Exception:
        return _fail(provider, 'userinfo')

    email = (ui.get('email') or '').strip().lower()
    full_name = (
        ui.get('name')
        or f"{ui.get('given_name', '')} {ui.get('family_name', '')}".strip()
    )
    if not email:
        # Facebook peut ne pas renvoyer d'email si l'utilisateur l'a masqué
        return _fail(provider, 'noemail')

    user = _get_or_create_social_user(email, full_name)
    if not user.is_active:
        return _fail(provider, 'disabled')

    # c) pose TES cookies JWT et renvoie vers le front (connecté)
    refresh, access = get_tokens_for_user(user)
    response = HttpResponseRedirect(f'{FRONTEND_URL}/')
    set_auth_cookies(response, access, refresh)
    return response
