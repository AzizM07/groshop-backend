from users.models import User
from products.models import Product, Review, ReviewPhoto
from django.db.models import Avg, Count
import random

buyer2, created = User.objects.get_or_create(
    email='buyer2@test.tn',
    defaults={'full_name': 'Amira Khelifi', 'role': 'buyer', 'is_active': True, 'is_verified': True}
)
if created:
    buyer2.set_password('TestPass123!')
    buyer2.save()
    print('buyer2@test.tn créé')
else:
    print('buyer2@test.tn existait déjà')

buyer1 = User.objects.get(email='buyer@test.tn')

REVIEW_TEXTS = [
    (5, "Excellent produit, exactement comme décrit. Livraison rapide et emballage soigné. Je recommande vivement ce fournisseur."),
    (4, "Bon rapport qualité-prix. Quelques jours de délai en plus que prévu mais le résultat en vaut la peine."),
    (5, "Très satisfait de mon achat. La qualité est au rendez-vous et le service client a été réactif tout au long du processus."),
    (3, "Correct sans plus. Le produit fait le travail mais j'attendais un peu mieux niveau finition pour ce prix."),
    (5, "Parfait pour mon commerce, j'en ai commandé plusieurs fois déjà. Qualité constante, fournisseur sérieux."),
    (4, "Conforme à la description, bon emballage. Je recommande pour les commandes en volume."),
]

products = list(Product.objects.filter(status='approved'))
print(f'{len(products)} produits trouvés.')

created_count = 0
for product in products:
    buyers = [buyer1, buyer2]
    random.shuffle(buyers)
    n_reviews = random.choice([1, 2])
    for buyer in buyers[:n_reviews]:
        rating, text = random.choice(REVIEW_TEXTS)
        # IMPORTANT: supplier=None ici — un avis lié à un PRODUIT
        # ne doit pas remplir "supplier", sinon la contrainte
        # unique_review_supplier bloque dès le 2e produit du
        # même fournisseur. "supplier" est réservé aux avis
        # génériques sur la boutique (sans produit associé).
        review, was_created = Review.objects.get_or_create(
            reviewer=buyer,
            product=product,
            defaults={'supplier': None, 'rating': rating, 'comment': text}
        )
        if was_created:
            created_count += 1
            print('  + avis sur', product.name, 'par', buyer.full_name, rating)

print(created_count, 'avis créés au total.')

for product in products:
    stats = Review.objects.filter(product=product).aggregate(avg=Avg('rating'), count=Count('id'))
    product.rating_avg = round(stats['avg'] or 0, 2)
    product.rating_count = stats['count'] or 0
    product.save(update_fields=['rating_avg', 'rating_count'])

print('rating_avg / rating_count recalculés.')

SAMPLE_PHOTOS = [
    "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&q=70",
    "https://images.unsplash.com/photo-1591290619762-c2e9c8de9d09?w=400&q=70",
    "https://images.unsplash.com/photo-1622957461293-1cfb0b1d4c79?w=400&q=70",
    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=70",
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=70",
]

reviews = list(Review.objects.all())
photos_added = 0
for review in reviews:
    if not review.photos.exists() and random.random() < 0.5:
        n_photos = random.choice([1, 2, 3])
        photos = random.sample(SAMPLE_PHOTOS, n_photos)
        for i, url in enumerate(photos):
            ReviewPhoto.objects.get_or_create(review=review, url=url, defaults={'sort_order': i})
            photos_added += 1

print(photos_added, 'photos ajoutées.')
print('TOTAL avis:', Review.objects.count())
print('TOTAL photos:', ReviewPhoto.objects.count())