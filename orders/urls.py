# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                  views.orders_list,   name='orders-list'),
    path('create/',           views.create_order,  name='create-order'),
    path('<uuid:pk>/',        views.order_detail,  name='order-detail'),
    path('<uuid:pk>/cancel/', views.cancel_order,  name='cancel-order'),
]