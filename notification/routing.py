# notification/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notification/(?P<user_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]