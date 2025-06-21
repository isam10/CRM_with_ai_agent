from django.urls import re_path
from crm_features.consumers import ChatConsumer

websockets_urlpatterns =[
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]