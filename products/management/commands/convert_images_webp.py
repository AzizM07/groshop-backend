# <une_app>/management/commands/convert_images_webp.py
#
# Convertit les images DÉJÀ en ligne (Supabase) en WebP et met à jour la base.
# Place ce fichier dans :  <une_app>/management/commands/convert_images_webp.py
# (avec un __init__.py vide dans management/ ET dans management/commands/)
#
# Usage :
#   python manage.py convert_images_webp --dry-run          # aperçu, ne modifie rien
#   python manage.py convert_images_webp --limit 3          # test : 3 par cible
#   python manage.py convert_images_webp                    # tout convertir
#   python manage.py convert_images_webp --delete-old       # + supprime les anciens (champs "file" only)
#
# ⚠️ SAUVEGARDE ta base avant (dump). Fais --dry-run, puis --limit petit, vérifie
#    que les images s'affichent, et seulement après lance le run complet.
#    Ne mets --delete-old qu'une fois que TOUT est vérifié.

import io
import uuid
from urllib.parse import urlparse, unquote
from urllib.request import urlopen, Request

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.apps import apps

from PIL import Image

MAX_DIM = 1600
QUALITY = 82

# Cibles : ('app_label.Model', 'champ', kind, 'dossier_destination')
#   kind='file' → ImageField/FileField (obj.champ.name = clé storage)
#   kind='url'  → CharField/TextField/URLField contenant une URL publique Supabase
TARGETS = [
    ('banners.Banner',        'image',         'file', 'banners'),
    ('banners.BannerImage',   'image',         'file', 'banners'),
    ('banners.BannerImage',   'image_url_ext', 'url',  'banners'),
    ('products.Category',     'image_url',     'url',  'categories'),
    ('products.Category',     'banner_url',    'url',  'categories'),
    ('products.ProductImage', 'url',           'url',  'products'),
    ('products.ProductVariant', 'image_url',   'url',  'products'),
    # ('products.ReviewPhoto', 'url',          'url',  'reviews'),   # photos d'avis clients — décommente si tu veux les inclure
]


def to_webp(raw_bytes):
    img = Image.open(io.BytesIO(raw_bytes))
    img = img.convert('RGB') if img.mode in ('RGBA', 'P') else img
    img.thumbnail((MAX_DIM, MAX_DIM))
    buf = io.BytesIO()
    img.save(buf, format='WEBP', quality=QUALITY)
    buf.seek(0)
    return buf.read()


def http_get(url):
    req = Request(url, headers={'User-Agent': 'groshop-webp-migration'})
    with urlopen(req, timeout=30) as r:
        return r.read()


def read_source(value, kind):
    """Retourne (bytes, ancien_nom) ; ancien_nom sert pour --delete-old (kind file)."""
    if kind == 'file':
        name = value.name
        with default_storage.open(name, 'rb') as fh:
            return fh.read(), name
    raw = http_get(value)
    return raw, unquote(urlparse(value).path)


def save_webp(webp_bytes, folder):
    """Enregistre le WebP avec le bon content-type (sinon Supabase = octet-stream)."""
    key = f'{folder}/{uuid.uuid4().hex}.webp'
    cf = ContentFile(webp_bytes, name=f'{uuid.uuid4().hex}.webp')
    cf.content_type = 'image/webp'          # ← corrige le MIME
    saved = default_storage.save(key, cf)
    return saved, default_storage.url(saved)


class Command(BaseCommand):
    help = 'Convertit les images existantes (Supabase) en WebP et met à jour la base.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Affiche ce qui serait fait sans rien modifier.')
        parser.add_argument('--delete-old', action='store_true',
                            help='Supprime l’ancien fichier après conversion (champs "file" uniquement).')
        parser.add_argument('--limit', type=int, default=0,
                            help='Limiter le nombre de conversions par cible (pour tester).')

    def handle(self, *args, **opts):
        dry = opts['dry_run']
        for dotted, field, kind, folder in TARGETS:
            app_label, model_name = dotted.split('.')
            try:
                Model = apps.get_model(app_label, model_name)
            except LookupError:
                self.stderr.write(self.style.WARNING(f'Modèle introuvable, ignoré : {dotted}'))
                continue

            done = 0
            for obj in Model.objects.all().iterator():
                value = getattr(obj, field, None)
                ref = value.name if (kind == 'file' and value) else value
                if not ref:
                    continue
                if str(ref).lower().split('?')[0].endswith('.webp'):
                    continue  # déjà en webp

                try:
                    raw, old_name = read_source(value, kind)
                    webp = to_webp(raw)
                except Exception as e:
                    self.stderr.write(f'  ✗ {dotted}#{obj.pk} {field}: {e}')
                    continue

                if dry:
                    self.stdout.write(f'  [dry] {dotted}#{obj.pk} {field}  →  {folder}/xxxx.webp')
                else:
                    saved, new_url = save_webp(webp, folder)
                    if kind == 'file':
                        setattr(obj, field, saved)     # ImageField stocke la clé storage
                    else:
                        setattr(obj, field, new_url)   # champ URL stocke l'URL publique
                    obj.save(update_fields=[field])

                    if opts['delete_old'] and kind == 'file':
                        try:
                            default_storage.delete(old_name)
                        except Exception:
                            pass

                    self.stdout.write(f'  ✓ {dotted}#{obj.pk} {field}  →  {new_url}')

                done += 1
                if opts['limit'] and done >= opts['limit']:
                    break

            self.stdout.write(self.style.SUCCESS(f'{dotted}.{field} : {done} converti(s)'))