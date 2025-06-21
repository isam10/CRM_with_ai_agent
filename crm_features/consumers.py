from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async 
import json
import asyncio

from .models import Chatroom, Message
from .config.redis import redis_client
from .ai.query_agents import process_query


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room = await self.get_or_create_room(self.room_name)

        await self.accept()

        messages = redis_client.lrange(self.room_name, -20, -1)
        for message in messages:
            parsed_message = json.loads(message)
            await self.send(text_data=json.dumps(parsed_message))

    async def disconnect(self, close_code):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        query = data.get('query')

        user_message = {
            'sender': 'User',
            'content': query,
            'timestamp': str(now())
        }
        redis_client.rpush(self.room_name, json.dumps(user_message))
        await self.save_message(self.room, 'User', query)

        result = process_query(query)

        bot_message = {
            'sender': 'AI',
            'content': result,
            'timestamp': str(now())
        }
        redis_client.rpush(self.room_name, json.dumps(bot_message))
        await self.save_message(self.room, 'AI', result)

        await self.send(text_data=json.dumps(bot_message))

    @sync_to_async
    def get_or_create_room(self, room_name):
        return Chatroom.objects.get_or_create(room_name=room_name)[0]

    @sync_to_async
    def save_message(self, room, sender, content):
        Message.objects.create(room=room, sender=sender, content=content, timestamp=now())
