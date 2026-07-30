from django.urls import path
from . import views

urlpatterns = [
    path('register/',        views.register_token,      name='notifications-register'),
    path('unregister/',      views.unregister_token,    name='notifications-unregister'),
    path('admin/',           views.admin_notifications, name='notifications-admin'),
    path('admin/stats/',     views.admin_stats,         name='notifications-admin-stats'),
]