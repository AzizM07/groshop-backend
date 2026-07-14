# analytics/urls.py — GROSHOP.tn
# À inclure dans le urls.py racine :
#   path('api/analytics/', include('analytics.urls')),

from django.urls import path
from . import views

urlpatterns = [
    # ── Tracking (public) ──
    path('pageview/',              views.track_pageview,                     name='track-pageview'),

    # ── Stats fournisseur ──
    path('supplier/stats/',        views.SupplierAnalyticsView.as_view(),    name='supplier-analytics'),
    path('supplier/active-users/', views.SupplierActiveUsersView.as_view(),  name='supplier-active-users'),
    path('supplier/regions/',      views.SupplierRegionStatsView.as_view(),  name='supplier-regions'),
    path('supplier/target/',       views.CurrentMonthTargetView.as_view(),   name='supplier-target'),

    # ── Objectifs (CRUD) ──
    path('targets/',               views.MonthlyTargetListCreateView.as_view(), name='targets-list'),
    path('targets/<int:pk>/',      views.MonthlyTargetDetailView.as_view(),     name='targets-detail'),
]