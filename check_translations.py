from products.models import Product, Category, ProductVariant, ProductChoiceGroup

print("=" * 70)
print("CATEGORIES")
print("=" * 70)
for c in Category.objects.all():
    print(f"FR: {c.name_fr!r:40} EN: {c.name_en!r:40} AR: {c.name_ar!r}")

print()
print("=" * 70)
print("PRODUITS (name)")
print("=" * 70)
for p in Product.objects.all():
    print(f"FR: {p.name_fr!r:40} EN: {p.name_en!r:40} AR: {p.name_ar!r}")

print()
print("=" * 70)
print("PRODUITS (description)")
print("=" * 70)
for p in Product.objects.all():
    print(f"FR: {(p.description_fr or '')[:40]!r:45} EN: {(p.description_en or '')[:40]!r:45} AR: {(p.description_ar or '')[:40]!r}")

print()
print("=" * 70)
print("VARIANTES")
print("=" * 70)
for v in ProductVariant.objects.all():
    print(f"FR: {v.name_fr!r:40} EN: {v.name_en!r:40} AR: {v.name_ar!r}")

print()
print("=" * 70)
print("GROUPES DE CHOIX")
print("=" * 70)
for g in ProductChoiceGroup.objects.all():
    print(f"FR: {g.name_fr!r:40} EN: {g.name_en!r:40} AR: {g.name_ar!r}")