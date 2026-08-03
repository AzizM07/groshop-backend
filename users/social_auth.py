# users/social_auth.py — GROSHOP.tn
# Connexion sociale (Google / Facebook / LinkedIn).
#
# Deux flux cohabitent :
#   • REDIRECTION SERVEUR (Google, LinkedIn) : /start/ -> provider -> /callback/
#   • TOKEN CLIENT (Facebook) : le front obtient l'access_token via le SDK JS
#     (FB.login popup) puis le POST à /facebook/token/. AUCUNE navigation vers
#     le callback -> plus de page rouge "Site dangereux" de Chrome.
#
# Aucune session Django n'est utilisée pour l'auth : on réutilise exactement
# tes helpers cookies (set_auth_cookies / get_tokens_for_user) de views.py.
# La session ne sert qu'à stocker le "state" anti-CSRF le temps de l'aller-retour.

import json
import secrets
import urllib.parse
import requests as http

from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
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
        'scope':         'email',
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


# ── 3) Facebook — flux TOKEN CLIENT (SDK JS, pas de redirection) ──
@csrf_exempt
@require_POST
def facebook_token(request):
    """
    Le front envoie { access_token } obtenu via FB.login (SDK JS).
    On VÉRIFIE le token côté Graph (debug_token = anti-usurpation), on récupère
    email + nom, on pose les cookies JWT, et on renvoie l'utilisateur en JSON.
    Aucune navigation vers /callback/ -> Chrome n'affiche jamais la page rouge.
    """
    cfg = PROVIDERS['facebook']
    if not cfg['client_id'] or not cfg['client_secret']:
        return JsonResponse({'error': 'notconfigured'}, status=503)

    # token envoyé en JSON ou en form-data
    access_token = ''
    if request.content_type and 'application/json' in request.content_type:
        try:
            access_token = (json.loads(request.body or '{}').get('access_token') or '').strip()
        except Exception:
            access_token = ''
    else:
        access_token = (request.POST.get('access_token') or '').strip()

    if not access_token:
        return JsonResponse({'error': 'token'}, status=400)

    app_token = f"{cfg['client_id']}|{cfg['client_secret']}"

    # a) VÉRIFIE que le token a bien été émis pour NOTRE app (anti-substitution)
    try:
        dbg = http.get(
            'https://graph.facebook.com/debug_token',
            params={'input_token': access_token, 'access_token': app_token},
            timeout=10,
        ).json().get('data', {})
    except Exception:
        return JsonResponse({'error': 'token'}, status=400)

    if not dbg.get('is_valid') or str(dbg.get('app_id')) != str(cfg['client_id']):
        return JsonResponse({'error': 'token'}, status=401)

    # b) profil (email + nom) via Graph
    try:
        ui = http.get(
            cfg['userinfo'],
            params={'access_token': access_token},
            timeout=10,
        ).json()
    except Exception:
        return JsonResponse({'error': 'userinfo'}, status=502)

    email = (ui.get('email') or '').strip().lower()
    full_name = ui.get('name') or ''
    if not email:
        return JsonResponse({'error': 'noemail'}, status=400)

    user = _get_or_create_social_user(email, full_name)
    if not user.is_active:
        return JsonResponse({'error': 'disabled'}, status=403)

    # c) pose TES cookies JWT et renvoie l'utilisateur (le front fait setUser)
    refresh, access = get_tokens_for_user(user)
    resp = JsonResponse({
        'user': {
            'id':        str(user.id),
            'email':     user.email,
            'full_name': user.full_name,
            'role':      user.role,
        }
    })
    set_auth_cookies(resp, access, refresh)
    return resp