from django.urls import path
from . import views

urlpatterns = [
    path('register/buyer/',                 views.register_buyer,    name='register-buyer'),
    path('register/supplier/',              views.register_supplier, name='register-supplier'),
    path('login/',                          views.login,             name='login'),
    path('refresh/',                        views.refresh_view,      name='refresh'),
    path('me/',                             views.me,                name='me'),
    path('logout/',                         views.logout,            name='logout'),
    path('google/',                         views.google_one_tap,    name='google-one-tap'),
    path('supplier/me/',                    views.supplier_me,       name='supplier-me'),
    path('suppliers/<slug:slug>/',          views.supplier_public,   name='supplier-public'),
    path('suppliers/<slug:slug>/products/', views.supplier_products, name='supplier-products'),
]