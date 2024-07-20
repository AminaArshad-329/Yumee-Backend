from django.contrib.auth.models import User
from rest_framework import serializers
from core.serializers import ProfilePostSerializer
from .models import *


class ChatSerializer(serializers.ModelSerializer):
    # receiver = ProfilePostSerializer()
    # sender = ProfilePostSerializer()
    class Meta:
        model = chat
        fields = '__all__'


class ChatListSerializer(serializers.ModelSerializer):
    receiver = ProfilePostSerializer()
    sender = ProfilePostSerializer()

    class Meta:
        model = chat
        fields = '__all__'


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class ThreadSerializer(serializers.ModelSerializer):
    receiver = ProfilePostSerializer()
    sender = ProfilePostSerializer()

    class Meta:
        model = All_Threads
        fields = '__all__'


class ThreadSerializerData(serializers.ModelSerializer):
    class Meta:
        model = All_Threads
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    sender = ProfilePostSerializer()
    receiver = ProfilePostSerializer()

    class Meta:
        model = chat
        fields = '__all__'
