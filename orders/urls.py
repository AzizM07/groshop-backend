# orders/urls.py
from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('',        views.orders_list,  name='orders-list'),
    path('create/', views.create_order, name='create-order'),
    path('cart/merge/', views.cart_merge, name='cart-merge'),

    # ── Espace fournisseur (avant <uuid:pk>) ──
    path('supplier/',            views.supplier_orders,          name='supplier-orders'),
    path('supplier/<uuid:pk>/',  views.supplier_suborder_update, name='supplier-suborder-update'),
    path('admin/products/<uuid:product_id>/specs/', admin_views.admin_update_product_specs),

    # ── Customization requests (devis perso) ── ← AJOUT
    path('customization-requests/',                       views.customization_requests,         name='customization-requests'),
    path('customization-requests/<uuid:pk>/quote/',       views.customization_request_quote,    name='customization-request-quote'),
    path('customization-requests/<uuid:pk>/accept/',      views.customization_request_accept,   name='customization-request-accept'),
    path('customization-requests/<uuid:pk>/reject/',      views.customization_request_reject,   name='customization-request-reject'),

    # ── Acheteur (UUID) ──
    path('to-review/',        views.to_review,     name='orders-to-review'),
    path('<uuid:pk>/',        views.order_detail,  name='order-detail'),
    path('<uuid:pk>/cancel/', views.cancel_order,  name='cancel-order'),
]