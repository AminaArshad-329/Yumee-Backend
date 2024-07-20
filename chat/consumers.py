# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = self.room_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'data': text_data_json
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        data = event
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'data': data
        }))

    # Receive message from room group
    def message_seen_status(self, event):
        sender_read_status = event['manage_read_receipts']
        data = event
        self.send(text_data=json.dumps({
            'sender_read_status': sender_read_status
        }))
