import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'alerts_{self.user_id}'
        
        # Check if the user exists
        user_exists = await self.user_exists(self.user_id)
        if not user_exists:
            await self.close()
            return
        
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # We don't expect to receive messages from clients
        pass
    
    async def alert_message(self, event):
        # Send the alert message to the WebSocket
        await self.send(text_data=json.dumps(event['message']))
    
    @database_sync_to_async
    def user_exists(self, user_id):
        try:
            return User.objects.filter(id=user_id).exists()
        except:
            return False
