from django.core.management.base import BaseCommand
from products import search

class Command(BaseCommand):
    help = "Réindexe tous les produits dans Meilisearch"

    def handle(self, *args, **opts):
        n = search.reindex_all()
        self.stdout.write(self.style.SUCCESS(f"{n} produits indexés."))