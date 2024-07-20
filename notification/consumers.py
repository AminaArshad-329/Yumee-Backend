# notification/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope['url_route']['kwargs'])
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notification_group_name = 'user_notification_%s' % self.user_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.notification_group_name,
            {
                'type': 'notification',
                'message': message,
                'data': text_data_json
            }
        )

    # Receive message from room group
    def notification(self, event):
        message = event['message']
        data=event

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'data':data
        }))