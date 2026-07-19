# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.orders_list,             name='orders-list'),
    path('create/',              views.create_order,            name='create-order'),

    # ── Espace fournisseur (avant <uuid:pk>) ──
    path('supplier/',            views.supplier_orders,          name='supplier-orders'),
    path('supplier/<uuid:pk>/',  views.supplier_suborder_update, name='supplier-suborder-update'),

    # ── Acheteur (UUID) ──
    path('to-review/', views.to_review, name='orders-to-review'),
    path('<uuid:pk>/',        views.order_detail,  name='order-detail'),
    path('<uuid:pk>/cancel/', views.cancel_order,  name='cancel-order'),
]