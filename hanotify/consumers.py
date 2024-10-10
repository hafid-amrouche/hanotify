# your_app_name/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async


@database_sync_to_async
def get_store_from_user_token(store_id, token_key):
        # Retrieve user based on the authentication token
        from user.models import UserToken
        try:
            user = UserToken.objects.get( token=token_key ).user
            store = user.stores.get(id=store_id)
            return store
        except:
            return None

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):        
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_parameters = parse_qs(query_string)
        token = query_parameters.get("token", [""])[0]
        store_id = query_parameters.get("store_id", [""])[0]
        store = get_store_from_user_token(token, store_id)
        if not store:
            self.disconnect()
        else:
            self.room_group_name = f'orders-{store_id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"Orders of store {store_id} is connected.")


    async def disconnect(self, close_code):
        # Leave room group
        pass

    # Receive message from room group
    async def send_new_order(self, event):
        print(f"STEP-2")
        order = event['order']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'order': order
        }))
 
