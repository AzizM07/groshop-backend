from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

# Enregistre tous les modèles de l'app users automatiquement
from django.apps import apps
for model in apps.get_app_config('users').get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass