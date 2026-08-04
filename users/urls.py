from django.urls import path
from . import views
from . import social_auth
from . import phone_verify

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

    # ── Espace fournisseur (vitrine) ──
    path('supplier/me/',                    views.supplier_me,           name='supplier-me'),
    path('supplier/store/',                 views.supplier_update_store, name='supplier-update-store'),
    path('supplier/store/upload/',          views.supplier_store_upload, name='supplier-store-upload'),

    path('suppliers/<slug:slug>/',          views.supplier_public,   name='supplier-public'),
    path('suppliers/<slug:slug>/products/', views.supplier_products, name='supplier-products'),

    path('addresses/',                    views.addresses_list,       name='addresses_list'),
    path('addresses/<uuid:pk>/',          views.address_detail,       name='address_detail'),
    path('addresses/<uuid:pk>/default/',  views.address_set_default,  name='address_set_default'),

    # ── Vérification du téléphone (OTP) ──
    path('phone/request-otp/', phone_verify.request_phone_otp, name='phone-request-otp'),
    path('phone/verify-otp/',  phone_verify.verify_phone_otp,  name='phone-verify-otp'),

    path('facebook/token/',          social_auth.facebook_token,  name='facebook-token'),

    # ⚠️ Ces deux routes génériques doivent rester EN DERNIER : <str:provider>
    #    matche n'importe quel segment, donc toute route spécifique (phone/, facebook/…)
    #    doit être déclarée avant, sinon elle serait avalée par 'provider'.
    path('<str:provider>/start/',    social_auth.social_start),
    path('<str:provider>/callback/', social_auth.social_callback),
]