# groshop/middleware.py
from django.utils import translation

class ActiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang') or request.headers.get('X-Lang') or 'fr'
        if lang not in ('fr', 'en', 'ar'):   # ← ajout 'en'
            lang = 'fr'
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        translation.deactivate()
        return response