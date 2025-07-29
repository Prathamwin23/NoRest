import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated or self.user.role != 'agent':
            await self.close()
            return

        self.group_name = f'agent_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'location_update':
                await self.handle_location_update(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))

    async def handle_location_update(self, data):
        try:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            await self.send(text_data=json.dumps({
                'type': 'location_updated',
                'message': 'Location updated successfully'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))

class ManagerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated or self.user.role != 'manager':
            await self.close()
            return

        self.group_name = f'manager_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add('managers', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('managers', self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
