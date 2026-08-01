# messaging/urls.py — GROSHOP.tn
from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.conversations_list,   name='conversations-list'),
    path('unread-count/',               views.unread_count,         name='unread-count'),
    path('<uuid:pk>/',                  views.conversation_detail,  name='conversation-detail'),
    path('<uuid:pk>/poll/',             views.conversation_poll,    name='conversation-poll'),
    path('<uuid:pk>/send/',             views.send_message,         name='send-message'),
    path('start/<slug:supplier_slug>/', views.start_conversation,   name='start-conversation'),
]