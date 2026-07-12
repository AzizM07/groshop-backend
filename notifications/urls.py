from django.urls import path
from . import views

urlpatterns = [
    path('',              views.notifications_list, name='notifications-list'),
    path('<uuid:pk>/read/', views.mark_read,        name='mark-read'),
    path('read-all/',     views.mark_all_read,      name='mark-all-read'),
]