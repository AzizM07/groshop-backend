from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ═══════════════════════════════════════════════════════════════════
# CORE
# ═══════════════════════════════════════════════════════════════════
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# ⭐ Sécurisé : plus de '*'
# En local, mettre dans .env : ALLOWED_HOSTS=localhost,127.0.0.1
# En prod (Render) : ALLOWED_HOSTS=groshop.tn,www.groshop.tn,api.groshop.tn,.onrender.com
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# ═══════════════════════════════════════════════════════════════════
# APPS
# ═══════════════════════════════════════════════════════════════════
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',  # ⭐ pour R2/S3 (optionnel — commente si tu n'utilises pas encore)

    # Apps GROSHOP
    'users',
    'products',
    'orders',
    'notifications',
    'messaging',
    'gamification',
    'store',
]


# ═══════════════════════════════════════════════════════════════════
# MIDDLEWARE (ordre important)
# ═══════════════════════════════════════════════════════════════════
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ⭐ AJOUTÉ juste après security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.LastSeenMiddleware',  # ⭐ DÉPLACÉ après AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'groshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'groshop.wsgi.application'


# ═══════════════════════════════════════════════════════════════════
# DATABASE — Neon PostgreSQL en prod, local en dev
# ═══════════════════════════════════════════════════════════════════
# Si DATABASE_URL existe (prod), on l'utilise. Sinon on utilise les vars séparées (dev).
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,           # Garde la connexion 10 min (perf)
            conn_health_checks=True,     # Vérifie que la connexion est vivante
            ssl_require=True,            # ⭐ Neon exige SSL
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     config('DB_NAME'),
            'USER':     config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST':     config('DB_HOST'),
            'PORT':     config('DB_PORT'),
        }
    }


# ═══════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'login': '5/min',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES':        ('Bearer',),
}


# ═══════════════════════════════════════════════════════════════════
# CORS + CSRF
# ═══════════════════════════════════════════════════════════════════
# Local + Prod — mets dans .env :
#   CORS_ALLOWED_ORIGINS=https://groshop.tn,https://www.groshop.tn
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://localhost:3000',
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:5173,http://localhost:3000',
    cast=Csv(),
)

# ⭐ Cookies plus stricts en prod (auto : Secure=True si pas DEBUG)
CSRF_COOKIE_HTTPONLY   = False
CSRF_COOKIE_SAMESITE   = 'Lax'
CSRF_COOKIE_SECURE     = not DEBUG      # ⭐ True en prod
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE  = not DEBUG      # ⭐ True en prod


# ═══════════════════════════════════════════════════════════════════
# SÉCURITÉ EN PROD
# ═══════════════════════════════════════════════════════════════════
if not DEBUG:
    # HTTPS forcé
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS — force HTTPS pendant 1 an
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Anti-clickjacking / XSS / MIME sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'


# ═══════════════════════════════════════════════════════════════════
# MOTS DE PASSE
# ═══════════════════════════════════════════════════════════════════
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ═══════════════════════════════════════════════════════════════════
# STATIC & MEDIA
# ═══════════════════════════════════════════════════════════════════
# ⭐ Static avec WhiteNoise (obligatoire sur Render)
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ⭐ MEDIA — deux modes possibles selon si tu configures R2/S3 ou pas
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # Cloudflare R2 (compatible S3) — pour les images uploadées
    AWS_ACCESS_KEY_ID     = config('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('R2_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL   = config('R2_ENDPOINT_URL')     # ex: https://xxx.r2.cloudflarestorage.com
    AWS_S3_CUSTOM_DOMAIN  = config('R2_CUSTOM_DOMAIN', default='')  # ex: cdn.groshop.tn
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/' if AWS_S3_CUSTOM_DOMAIN else f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
else:
    # Fallback local (dev)
    MEDIA_URL   = '/media/'
    MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ═══════════════════════════════════════════════════════════════════
# LOCALIZATION
# ═══════════════════════════════════════════════════════════════════
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Tunis'
USE_I18N      = True
USE_TZ        = True