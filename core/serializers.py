import os
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User_Profile, User_Picture, like_and_dislike, user_block, Countries, City
from chat.models import ChatRoom
from django.db.models import Q
from core.models import FilterHistory

class DatingChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Picture
        fields = ['id', 'picture']


class ProfilePostUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = '__all__'


class PhoneverfivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = ["registration_status", "verfication_status"]


class ResendOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = ['user', 'email', "otp", "verfication_status"]


class ProfilePostSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True, required=False)

    class Meta:
        model = User_Profile
        fields = ['id', 'user', 'email', 'your_name', 'gender', 'interested_in', 'age', 'city', 'height', 'education',
                  'about', 'passion', 'job_title', 'company', 'university', 'school', 'country', 'date_of_birth',
                  'living', 'location', 'role', 'kids', 'drink', 'smoke', 'exercise', 'religion', 'user_profile_pic',
                  'interested_age', 'max_interested_age', 'latitude', 'longitude', 'distance'
            , 'registration_status', 'verfication_status', 'cross_user_list', 'appear_to_other', 'time_list',
                  'popup_seen', 'manage_read_receipts', 'package', 'package_duration', 'package_date_start',
                  'package_date_end', 'manage_read_receipts_date_start', 'manage_read_receipts_date_end',
                  'manage_read_receipts_payment', 'is_banned', 'is_restored',
                  'fcm_token', 'package_name', 'classic_bonus_2chance', 'classic_bonus_power_like',
                  'classic_bonus_power_like_start', 'classic_bonus_power_like_end', 'vip_bonus_power_like',
                  'vip_bonus_power_like_start', 'vip_bonus_power_like_end', 'classic_bonus_guaranteed_match',
                  'classic_bonus_guaranteed_match_start', 'classic_bonus_guaranteed_match_end',
                  'classic_bonus_love_coach', 'vip_bonus_love_coach']

    def update(self, instance, validated_data):
        profile_pic = None
        if validated_data.get('user_profile_pic'):
            profile_pic = validated_data.pop('user_profile_pic')
        user_profile_obj = User_Profile.objects.filter(user=instance).update(**validated_data)
        if profile_pic is not None:
            for track_data in profile_pic:
                test = User_Profile.objects.get(user=instance)
                User_Picture.objects.create(user_profile=test, **track_data)
        return user_profile_obj


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True, required=False)

    class Meta:
        model = User_Profile
        fields = ['id', 'user', 'your_name', 'age', 'city', 'gender', 'interested_in', 'height', 'education', 'about',
                  'email', 'country', 'date_of_birth',
                  'passion', 'job_title', 'company', 'university', 'school', 'living', 'location', 'role', 'kids',
                  'drink', 'smoke', 'exercise', 'religion', 'registration_status', 'latitude', 'longitude', 'distance',
                  'appear_to_other', 'interested_age', 'user_profile_pic', 'is_banned', 'is_restored'
            , 'max_interested_age', 'popup_seen', 'manage_read_receipts', 'package', 'package_duration',
                  'package_date_start', 'package_date_end', 'manage_read_receipts_date_start',
                  'manage_read_receipts_date_end', 'manage_read_receipts_payment', 'fcm_token'
            , 'package_name', 'classic_bonus_2chance', 'classic_bonus_power_like', 'classic_bonus_power_like_start',
                  'classic_bonus_power_like_end', 'vip_bonus_power_like', 'vip_bonus_power_like_start',
                  'vip_bonus_power_like_end', 'classic_bonus_guaranteed_match', 'classic_bonus_guaranteed_match_start',
                  'classic_bonus_guaranteed_match_end', 'classic_bonus_love_coach', 'vip_bonus_love_coach']

    def update(self, instance, validated_data):
        profile_pic = None
        if validated_data.get('user_profile_pic'):
            profile_pic = validated_data.pop('user_profile_pic')
        user_profile_obj = User_Profile.objects.filter(user=instance).update(**validated_data)
        if profile_pic is not None:
            for track_data in profile_pic:
                test = User_Profile.objects.get(user=instance)
                User_Picture.objects.create(user_profile=test, **track_data)
        return user_profile_obj


class ProfileScreenSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True, required=False)
    chat_room_data = serializers.SerializerMethodField()

    class Meta:
        model = User_Profile
        fields = ['id', 'email', 'your_name', 'age', 'city', 'education', 'about', 'location', 'job_title',
                  'user_profile_pic', 'passion', 'latitude', 'longitude', 'country', 'chat_room_data',
                  'is_banned', 'is_restored']

    def get_chat_room_data(self, obj):
        user_obj = User_Profile.objects.get(email=self.context['request'].user)
        liked_by = User_Profile.objects.get(email=obj)
        chat_data = ChatRoom.objects.filter(Q(user1=liked_by.id, user2=user_obj.id, is_deleed=False, is_enabled=True)
                                            | Q(user1=user_obj.id, user2=liked_by.id, is_deleed=False, is_enabled=True))
        return DatingChatSerializer(chat_data, many=True).data


class LikeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = like_and_dislike
        fields = ['user', 'user_profile_liked_or_dislike', 'profile_status', 'cross_check_user', 'created_date',
                  'modified_date']


class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_block
        fields = ['user', 'user_profile_block', 'profile_status', 'reasion']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['country_name', 'code']


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city_name']


class PicturePostSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True, required=False)
    id = serializers.IntegerField()

    class Meta:
        model = User_Profile
        fields = ['id', 'user', 'email', 'your_name', 'gender', 'interested_in', 'age', 'city', 'country', 'height',
                  'education', 'date_of_birth',
                  'about', 'passion', 'job_title', 'company', 'university', 'school', 'living', 'location', 'role',
                  'kids', 'drink', 'smoke', 'exercise', 'religion', 'user_profile_pic', 'interested_age',
                  'max_interested_age', 'latitude', 'longitude', 'distance', 'registration_status',
                  'verfication_status', 'cross_user_list', 'appear_to_other', 'time_list', 'popup_seen',
                  'manage_read_receipts', 'is_banned', 'is_restored',
                  'package', 'package_duration', 'package_date_start', 'package_date_end',
                  'manage_read_receipts_date_start', 'manage_read_receipts_date_end', 'manage_read_receipts_payment']

    def update(self, instance, validated_data):
        profile_pic = validated_data.pop('user_profile_pic')
        user_id = validated_data.pop('id')
        user_profile_obj = User_Profile.objects.filter(user=instance)
        test = User_Profile.objects.get(user=instance)
        old_image = User_Picture.objects.filter(id=user_id).first()
        new_path = old_image.picture.path
        if profile_pic:
            os.remove(new_path)
            User_Picture.objects.filter(user_profile=test, id=user_id).update(picture=profile_pic)
        return user_profile_obj


class DatingSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True)
    chat_room = serializers.SerializerMethodField()

    class Meta:
        model = User_Profile
        fields = "__all__"

    def get_chat_room(self, obj):
        user_obj = User_Profile.objects.get(email=self.context['request'].user)
        liked_by = User_Profile.objects.get(email=obj)
        chat_data = ChatRoom.objects.filter(user1=liked_by.id, user2=user_obj.id, is_deleed=False, is_enabled=True)
        return DatingChatSerializer(chat_data, many=True).data


class UserChatProfileSerializer(serializers.ModelSerializer):
    user_profile_pic = UserPictureSerializer(many=True)

    class Meta:
        model = User_Profile
        fields = ['id', 'your_name', 'gender', 'email', 'user_profile_pic']

class FilterHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterHistory
        fields = '__all__'