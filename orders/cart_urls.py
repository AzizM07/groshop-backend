# orders/cart_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',           views.cart_view,      name='cart'),         # GET / POST
    path('clear/',     views.cart_clear,     name='cart-clear'),   # DELETE
    path('count/',     views.cart_count,     name='cart-count'),   # GET
    path('<uuid:pk>/', views.cart_item_view, name='cart-item'),    # PATCH / DELETE
]