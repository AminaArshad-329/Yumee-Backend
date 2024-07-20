from django.contrib.auth.models import User
from core.models import User_Profile
from chat.models import ChatRoom
from admin_panel.models import Packages

from rest_framework import serializers


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_superuser']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = ['id', 'your_name', 'email', 'date_of_birth', 'age', 'gender', 'interested_in', 'religion',
                  'city', 'country', 'package', 'package_duration',
                  'package_date_start', 'package_date_end', 'remaining_days_in_exp']


class BlockedUserSerializer(serializers.ModelSerializer):
    blocked_user_name = serializers.CharField(source='block_user.your_name', read_only=True)
    block_by_username = serializers.CharField(source='block_by.your_name', read_only=True)
    blocked_user_email = serializers.EmailField(source='block_user.email', read_only=True)
    banned_status = serializers.BooleanField(source='block_user.is_banned', read_only=True)
    restore_status = serializers.BooleanField(source='block_user.is_restored', read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'room_name', 'block_user', 'blocked_user_email', 'blocked_user_name', 'block_by',
                  'block_by_username', 'banned_status', 'restore_status']


class PackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packages
        fields = ['id', 'name', 'duration', 'price']
