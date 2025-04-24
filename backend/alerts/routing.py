from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/alerts/(?P<user_id>\w+)/$', consumers.AlertConsumer.as_asgi()),
]
