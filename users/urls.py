from django.urls import path
from . import views
from . import social_auth
urlpatterns = [
    path('register/buyer/',                 views.register_buyer,    name='register-buyer'),
    path('register/supplier/',              views.register_supplier, name='register-supplier'),
    path('supplier-signup/',                views.supplier_signup,   name='supplier-signup'),
    path('upload-document/',                views.upload_document,   name='upload-document'),
    path('login/',                          views.login,             name='login'),
    path('refresh/',                        views.refresh_view,      name='refresh'),
    path('me/',                             views.me,                name='me'),
    path('logout/',                         views.logout,            name='logout'),
    path('google/',                         views.google_one_tap,    name='google-one-tap'),
    path('supplier/me/',                    views.supplier_me,       name='supplier-me'),
    path('suppliers/<slug:slug>/',          views.supplier_public,   name='supplier-public'),
    path('suppliers/<slug:slug>/products/', views.supplier_products, name='supplier-products'),
    path('addresses/',                    views.addresses_list,       name='addresses_list'),
    path('addresses/<uuid:pk>/',          views.address_detail,       name='address_detail'),
path('addresses/<uuid:pk>/default/',  views.address_set_default,  name='address_set_default'),
    path('<str:provider>/start/',    social_auth.social_start),
    path('<str:provider>/callback/', social_auth.social_callback),
]
