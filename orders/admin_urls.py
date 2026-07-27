# orders/admin_urls.py
# Monté à /api/admin/ dans le urls racine (à côté de users.admin_urls pour l'auth).
from django.urls import path
from . import admin_views

urlpatterns = [
    # KPIs + commandes
    path('stats/',                               admin_views.admin_stats,             name='admin_stats'),
    path('orders/',                              admin_views.admin_orders,            name='admin_orders'),
    path('orders/<uuid:sub_order_id>/',          admin_views.admin_order_detail,      name='admin_order_detail'),

    # Fournisseurs
    path('suppliers/',                           admin_views.admin_suppliers,         name='admin_suppliers'),
    path('suppliers/<uuid:supplier_id>/',        admin_views.admin_supplier_detail,   name='admin_supplier_detail'),
    path('suppliers/<uuid:supplier_id>/verify/', admin_views.admin_verify_supplier,   name='admin_verify_supplier'),

    # Produits
    path('products/',                            admin_views.admin_products,          name='admin_products'),
    path('products/<uuid:product_id>/',          admin_views.admin_product_detail,    name='admin_product_detail'),
    path('products/<uuid:product_id>/review/',   admin_views.admin_review_product,    name='admin_review_product'),

    # Utilisateurs
    path('users/',                               admin_views.admin_users,             name='admin_users'),
    path('users/<uuid:user_id>/',                admin_views.admin_user_detail,       name='admin_user_detail'),
    path('users/<uuid:user_id>/toggle-active/',  admin_views.admin_toggle_user_active, name='admin_toggle_user_active'),

    # Paiements
    path('payments/',                            admin_views.admin_payments,          name='admin_payments'),

    # Messagerie (surveillance)
    path('conversations/',                       admin_views.admin_conversations,       name='admin_conversations'),
    path('conversations/<uuid:conversation_id>/', admin_views.admin_conversation_detail, name='admin_conversation_detail'),
]