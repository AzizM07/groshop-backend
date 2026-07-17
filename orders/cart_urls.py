# orders/cart_urls.py — GROSHOP.tn
# Inclus dans groshop/urls.py :  path('api/cart/', include('orders.cart_urls')),

from django.urls import path
from . import views

urlpatterns = [
    path('',            views.cart_view,      name='cart'),          # GET liste · POST ajoute
    # ── routes statiques AVANT <uuid:pk> ──
    path('clear/',      views.cart_clear,     name='cart-clear'),    # DELETE vide tout
    path('count/',      views.cart_count,     name='cart-count'),    # GET badge nav
    path('<uuid:pk>/',  views.cart_item_view, name='cart-item'),     # PATCH qty · DELETE item
]