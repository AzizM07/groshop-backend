import json
import os
import firebase_admin
from firebase_admin import credentials, messaging, exceptions
from django.conf import settings

_app = None


def _get_app():
    global _app
    if _app is not None:
        return _app

    raw = settings.FIREBASE_CREDENTIALS
    if not raw:
        raise RuntimeError('FIREBASE_CREDENTIALS manquant (settings/env).')

    # Accepte 3 formes : dict déjà parsé, JSON en texte, ou chemin de fichier.
    if isinstance(raw, dict):
        cred = credentials.Certificate(raw)
    elif raw.strip().startswith('{'):
        cred = credentials.Certificate(json.loads(raw))
    elif os.path.exists(raw):
        cred = credentials.Certificate(raw)
    else:
        raise RuntimeError('FIREBASE_CREDENTIALS invalide : ni JSON, ni chemin existant.')

    _app = firebase_admin.initialize_app(cred)
    return _app


def _is_dead_token(exc):
    """True si le token doit être supprimé (désenregistré / introuvable)."""
    if isinstance(exc, messaging.UnregisteredError):
        return True
    code = getattr(exc, 'code', '')
    return code == 'NOT_FOUND' or 'not-registered' in str(exc).lower()


def send_to_tokens(tokens, title, body, image=None, link=None):
    """Envoie à une liste de tokens. Renvoie {success, failure, invalid[]}."""
    tokens = [t for t in tokens if t]
    if not tokens:
        return {'success': 0, 'failure': 0, 'invalid': []}

    _get_app()
    success = failure = 0
    invalid = []

    data = {'link': link} if link else {}

    webpush = messaging.WebpushConfig(
        notification=messaging.WebpushNotification(
            title=title, body=body, icon='/icons/icon-192.png', image=image or None,
        ),
        fcm_options=messaging.WebpushFCMOptions(link=link) if link else None,
    )

    # FCM limite chaque envoi multicast à 500 tokens
    for i in range(0, len(tokens), 500):
        chunk = tokens[i:i + 500]
        msg = messaging.MulticastMessage(
            tokens=chunk,
            notification=messaging.Notification(title=title, body=body, image=image or None),
            webpush=webpush,
            data=data,
        )
        resp = messaging.send_each_for_multicast(msg)
        success += resp.success_count
        failure += resp.failure_count
        for idx, r in enumerate(resp.responses):
            if not r.success and _is_dead_token(r.exception):
                invalid.append(chunk[idx])

    return {'success': success, 'failure': failure, 'invalid': invalid}