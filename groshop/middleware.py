# groshop/middleware.py
from django.utils import translation

ALLOWED_LANGS = {'fr', 'en', 'ar'}

class ActiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.headers.get('X-Lang', '').lower()
        if lang not in ALLOWED_LANGS:
            # fallback : user connecté → sa langue en base
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                lang = getattr(user, 'language', 'fr')
            else:
                lang = 'fr'
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        try:
            response = self.get_response(request)
        finally:
            translation.deactivate()
        return response