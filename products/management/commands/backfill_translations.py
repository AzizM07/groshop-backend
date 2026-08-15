"""
Commande de rattrapage : retraduit en masse toutes les lignes déjà en base
au moment où un champ a été ajouté à modeltranslation (specs_raw sur
Product, Banner, SubscriptionPlan, SupplierStore...).

Pourquoi c'est nécessaire :
Le signal post_save ne se déclenche QUE sur une nouvelle sauvegarde. Toute
ligne créée avant le branchement de la traduction auto reste avec ses
champs _en/_ar vides indéfiniment, sauf action explicite.

Usage :
    python manage.py backfill_translations                  # tout retraduit
    python manage.py backfill_translations --model product    # un seul modèle
    python manage.py backfill_translations --model category   # idem pour Category
    python manage.py backfill_translations --dry-run           # simulation, aucune écriture

Ne touche jamais un champ déjà traduit (auto_translate_fields ne remplace
jamais une traduction existante — manuelle ou automatique).
"""
from django.core.management.base import BaseCommand
from django.apps import apps

from products.translation_utils import auto_translate_fields


# ── Registre des modèles à retraduire, avec leurs champs sources ──
# Format : (app_label, model_name, [champs])
BACKFILL_TARGETS = [
    ('products', 'Product',            ['name', 'description', 'specs_raw']),
    ('products', 'Category',           ['name']),
    ('products', 'ProductVariant',     ['name']),
    ('products', 'ProductChoiceGroup', ['name']),
    ('banners',  'Banner',             ['title', 'tag', 'subtitle', 'cta_label']),
    ('store',    'SubscriptionPlan',   ['name']),
    ('users',    'SupplierStore',      [
        'description', 'hero_title', 'stats_title', 'stats_description',
        'about_title_main', 'about_title_accent', 'mission',
    ]),
]


class Command(BaseCommand):
    help = "Retraduit en masse (AWS Translate) toutes les lignes existantes n'ayant pas encore de traduction EN/AR."

    def add_arguments(self, parser):
        parser.add_argument(
            '--model', type=str, default=None,
            help="Ne traiter qu'un seul modèle (ex: product, category, banner, subscriptionplan, supplierstore).",
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help="N'écrit rien, affiche seulement ce qui serait traité.",
        )

    def handle(self, *args, **options):
        only_model = (options.get('model') or '').lower()
        dry_run = options.get('dry_run')

        targets = BACKFILL_TARGETS
        if only_model:
            targets = [t for t in targets if t[1].lower() == only_model]
            if not targets:
                self.stderr.write(self.style.ERROR(f"Modèle inconnu : {only_model}"))
                return

        total_processed = 0
        total_updated = 0

        for app_label, model_name, fields in targets:
            model_cls = apps.get_model(app_label, model_name)
            source_field = f'{fields[0]}_fr'  # ne traite que les lignes ayant un contenu source FR

            qs = model_cls.objects.exclude(**{f'{source_field}__isnull': True}) \
                                   .exclude(**{f'{source_field}__exact': ''})
            count = qs.count()
            self.stdout.write(f"→ {model_name} : {count} ligne(s) avec contenu FR à vérifier…")

            for obj in qs.iterator():
                total_processed += 1
                if dry_run:
                    continue
                try:
                    auto_translate_fields(model_cls, obj.pk, fields)
                    total_updated += 1
                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"  ⚠ {model_name} {obj.pk} : {e}"))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"[DRY RUN] {total_processed} ligne(s) auraient été traitées. Aucune écriture effectuée."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Terminé. {total_updated}/{total_processed} ligne(s) traitées avec succès."
            ))