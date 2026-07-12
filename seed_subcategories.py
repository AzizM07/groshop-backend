# seed_subcategories.py
# Lance avec : python manage.py shell
# Puis dans le shell : exec(open('seed_subcategories.py', encoding='utf-8').read())

from products.models import Category
from django.utils.text import slugify

SUBCATEGORIES = {
    'textile': [
        {'name': 'T-shirts',       'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400', 'is_hot': True},
        {'name': 'Jeans',          'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'},
        {'name': 'Robes',          'image_url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400', 'is_new': True},
        {'name': 'Vestes',         'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400'},
        {'name': 'Sous-vetements', 'image_url': 'https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=400'},
        {'name': 'Chaussures',     'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', 'is_hot': True},
        {'name': 'Sacs',           'image_url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400'},
    ],
    'electronique': [
        {'name': 'Smartphones',     'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400', 'is_hot': True},
        {'name': 'Accessoires',     'image_url': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400'},
        {'name': 'Audio',           'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'},
        {'name': 'Ordinateurs',     'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'},
        {'name': 'TV et Video',     'image_url': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400'},
        {'name': 'Petits electros', 'image_url': 'https://images.unsplash.com/photo-1574269909862-7e1d70bb892a?w=400', 'is_new': True},
    ],
    'alimentaire': [
        {'name': 'Epicerie',  'image_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=400'},
        {'name': 'Boissons',  'image_url': 'https://images.unsplash.com/photo-1543253687-c931c8e01820?w=400'},
        {'name': 'Conserves', 'image_url': 'https://images.unsplash.com/photo-1584473457409-ce95a9c00018?w=400'},
        {'name': 'Snacks',    'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 'is_hot': True},
        {'name': 'Surgeles',  'image_url': 'https://images.unsplash.com/photo-1574326830054-fab2cfae73c0?w=400'},
    ],
    'hygiene': [
        {'name': 'Soins du corps',   'image_url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400'},
        {'name': 'Hygiene dentaire', 'image_url': 'https://images.unsplash.com/photo-1559591935-c6c92c6bdd1f?w=400'},
        {'name': 'Bebe',             'image_url': 'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400', 'is_new': True},
        {'name': 'Detergents',       'image_url': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400'},
        {'name': 'Papier',           'image_url': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400'},
    ],
    'mobilier': [
        {'name': 'Salon',      'image_url': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400'},
        {'name': 'Chambre',    'image_url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400'},
        {'name': 'Cuisine',    'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400'},
        {'name': 'Bureau',     'image_url': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400', 'is_new': True},
        {'name': 'Decoration', 'image_url': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=400'},
    ],
    'beaute': [
        {'name': 'Maquillage',   'image_url': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400', 'is_hot': True},
        {'name': 'Parfums',      'image_url': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400'},
        {'name': 'Soins visage', 'image_url': 'https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400'},
        {'name': 'Cheveux',      'image_url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400'},
        {'name': 'Ongles',       'image_url': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400'},
    ],
    'sport': [
        {'name': 'Fitness',  'image_url': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400', 'is_hot': True},
        {'name': 'Football', 'image_url': 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=400'},
        {'name': 'Cyclisme', 'image_url': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400'},
        {'name': 'Natation', 'image_url': 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=400'},
        {'name': 'Outdoor',  'image_url': 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=400', 'is_new': True},
    ],
    'cuisine': [
        {'name': 'Ustensiles',    'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400'},
        {'name': 'Vaisselle',     'image_url': 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400'},
        {'name': 'Casseroles',    'image_url': 'https://images.unsplash.com/photo-1584990347449-a4d4e1b80b5c?w=400'},
        {'name': 'Petit electro', 'image_url': 'https://images.unsplash.com/photo-1574269909862-7e1d70bb892a?w=400'},
    ],
    'papeterie': [
        {'name': 'Ecriture',    'image_url': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400'},
        {'name': 'Cahiers',     'image_url': 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400'},
        {'name': 'Cartables',   'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400', 'is_hot': True},
        {'name': 'Bureautique', 'image_url': 'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=400'},
    ],
    'jouets': [
        {'name': 'Peluches',       'image_url': 'https://images.unsplash.com/photo-1559454403-b8fb88521f0e?w=400'},
        {'name': 'Jeux educatifs', 'image_url': 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400', 'is_new': True},
        {'name': 'Voitures',       'image_url': 'https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=400'},
        {'name': 'Poupees',        'image_url': 'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400'},
        {'name': 'Plein air',      'image_url': 'https://images.unsplash.com/photo-1597149083691-2a01b6e1bcad?w=400'},
    ],
}

print('Creation des sous-categories...')
print('')
created_count = 0
existing_count = 0

for parent_slug, subs in SUBCATEGORIES.items():
    try:
        parent = Category.objects.get(slug=parent_slug)
    except Category.DoesNotExist:
        print('  Parent introuvable : ' + parent_slug + ' - skip')
        continue

    print('--- ' + parent.name + ' ---')

    for i, sub_data in enumerate(subs):
        name = sub_data['name']
        slug = parent_slug + '-' + slugify(name)

        sub, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'parent':     parent,
                'name':       name,
                'image_url':  sub_data.get('image_url', ''),
                'is_hot':     sub_data.get('is_hot', False),
                'is_new':     sub_data.get('is_new', False),
                'sort_order': i,
                'is_active':  True,
            },
        )

        if created:
            print('  + ' + name)
            created_count += 1
        else:
            # Mise a jour de l'image si vide
            if not sub.image_url and sub_data.get('image_url'):
                sub.image_url = sub_data['image_url']
                sub.save()
            print('  = ' + name + ' (existe deja)')
            existing_count += 1
    print('')

print('Termine !')
print('  ' + str(created_count) + ' creees')
print('  ' + str(existing_count) + ' existaient deja')