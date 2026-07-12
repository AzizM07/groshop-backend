from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.conversations_list,   name='conversations-list'),
    path('<uuid:pk>/',                          views.conversation_detail,  name='conversation-detail'),
    path('<uuid:pk>/send/',                     views.send_message,         name='send-message'),
    path('start/<slug:supplier_slug>/',         views.start_conversation,   name='start-conversation'),
]