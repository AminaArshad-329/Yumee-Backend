# chat/urls.py
from django.urls import path
from . import views
from .views import ChatList, SendMessage, UpdateChat, DeleteChat, ChatRoomInfo, ThreadList, BlockMessage,\
    SendMessageSeen, ChatStatus

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_id>/', views.room, name='room'),
    # path('api/', Chat.as_view(), name="allchat"),
    path('api/chat_room_info/', ChatRoomInfo.as_view(), name="chat_rom_info"),
    path('api/send_message', SendMessage.as_view(), name="create"),
    # path('api/singleshatmessage/<str:pk>/', SingleChatMessage.as_view(), name="chatmessage"),
    path('api/list/', ChatList.as_view(), name="allchat"),
    # path('api/update/<str:pk>/', UpdateChat.as_view(), name="update"),
    path('api/update/', UpdateChat.as_view(), name="update"),
    path('api/delete/<int:pk>/', DeleteChat.as_view(), name="delete"),
    path('api/thread_list/', ThreadList.as_view(), name="thread_create"),
    path('api/block_message/', BlockMessage.as_view(), name="thread_create"),
    path('api/chat_status_check/', ChatStatus.as_view(), name='chat_status_check'),

    path('api/send_message_seen/', SendMessageSeen.as_view(), name="message_seen"),
]