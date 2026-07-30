import meilisearch
from django.conf import settings

client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILI_MASTER_KEY)
PRODUCTS_INDEX = "products"

# On indexe TOUT sauf ces statuts. Ajuste à tes vraies valeurs de Product.status
# si tu as d'autres statuts "non publics" (ex: 'rejected', 'archived', 'suspended').
HIDDEN_STATUSES = ("draft", "pending_review", "rejected", "archived")

def get_index():
    return client.index(PRODUCTS_INDEX)

def configure_index():
    """Réglages de pertinence — lancés aussi par reindex_all()."""
    get_index().update_settings({
        "searchableAttributes": ["name", "category_name", "supplier_name", "brand"],
        "filterableAttributes": ["category_name", "supplier_verified", "status"],
        "sortableAttributes":   ["sold_count", "base_price_tnd"],
        # à pertinence égale, le plus vendu remonte
        "rankingRules": ["words", "typo", "proximity", "attribute", "exactness", "sold_count:desc"],
        "typoTolerance": {
            "enabled": True,
            "minWordSizeForTypos": {"oneTypo": 3, "twoTypos": 6},
        },
    })

def _primary_image(p):
    imgs = list(p.images.all())
    for im in imgs:
        if im.is_primary:
            return im.url
    return imgs[0].url if imgs else None

def product_to_doc(p):
    return {
        "id":             str(p.id),
        "name":           p.name,
        "slug":           p.slug,
        "category_name":  p.category.name if p.category_id else None,
        "supplier_name":  getattr(p.supplier, "company_name", None) if p.supplier_id else None,
        "supplier_verified": getattr(p.supplier, "verification_status", None) if p.supplier_id else None,
        "brand":          p.brand or "",
        "base_price_tnd": float(p.base_price_tnd or 0),
        "sold_count":     p.sold_count or 0,
        "status":         p.status,
        "primary_image":  _primary_image(p),
    }

def index_product(p):
    """Ajoute/maj un produit — ou le retire s'il a un statut caché."""
    if p.status in HIDDEN_STATUSES:
        get_index().delete_document(str(p.id))
        return
    get_index().add_documents([product_to_doc(p)])

def delete_product(pk):
    get_index().delete_document(str(pk))

def reindex_all():
    """Réindexation complète : config + tous les produits visibles."""
    from .models import Product
    configure_index()
    qs = (Product.objects
          .exclude(status__in=HIDDEN_STATUSES)
          .select_related("category", "supplier")
          .prefetch_related("images"))
    docs = [product_to_doc(p) for p in qs]
    if docs:
        get_index().add_documents(docs)
    return len(docs)