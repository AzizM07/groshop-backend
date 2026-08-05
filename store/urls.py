# store/urls.py — GROSHOP.tn
# Inclus dans groshop/urls.py :  path('api/store/', include('store.urls')),

from django.urls import path
from . import views

urlpatterns = [
    path('recent-searches/',       views.recent_searches,       name='recent-searches'),
    path('recent-searches/clear/', views.clear_recent_searches, name='clear-recent-searches'),

    # ── Abonnement fournisseur (connecté) ──
    path('subscriptions/plans/',   views.plans_list,      name='plans-list'),
    path('subscriptions/me/',      views.my_subscription, name='my-subscription'),
    path('subscriptions/change/',  views.change_plan,     name='change-plan'),

    # ── Plans publics (landing, AllowAny) → /api/store/plans/ ──
    path('plans/',                 views.public_plans,    name='public-plans'),
]