from django.contrib.auth.models import User
from rest_framework import serializers
from core.serializers import ProfilePostSerializer
from .models import *

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'recever', 'text', 'created_date', 'modified_date', 'is_delete', 'is_seen']
        # fields = '__all__'


class NotificationRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRoomRoom
        # fields = ['id', 'sender', 'recever', 'text', 'created_date', 'modified_date', 'is_delete', 'is_seen']
        fields = '__all__'


class NotificationListSerializer(serializers.ModelSerializer):
    recever = ProfilePostSerializer()
    sender = ProfilePostSerializer()
    class Meta:
        model = Notification
        fields = '__all__'