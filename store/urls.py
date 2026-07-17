# store/urls.py — GROSHOP.tn
# À inclure dans groshop/urls.py :
#   path('api/store/', include('store.urls')),
 
from django.urls import path
from . import views
 
urlpatterns = [
    path('recent-searches/',       views.recent_searches,       name='recent-searches'),
    path('recent-searches/clear/', views.clear_recent_searches, name='clear-recent-searches'),
]
 