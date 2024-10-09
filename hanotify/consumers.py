# your_app_name/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room group
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard("orders", self.channel_name)

    # Receive message from room group
    async def send_new_order(self, event):
        order = event['order']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'order': order
        }))
