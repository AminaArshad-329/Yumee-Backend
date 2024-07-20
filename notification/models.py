from datetime import timezone
from django.contrib.auth.models import User
from django.db import models
from core.models import User_Profile,like_and_dislike
from django.contrib.auth import get_user_model

class NotificationRoomRoom(models.Model):
    # notification_room_name=models.CharField(max_length=100,null=True)
    user1=models.ForeignKey(User_Profile,related_name='notification_room_user1',on_delete=models.CASCADE)
    user2=models.ForeignKey(User_Profile,related_name='notification_room_user2',on_delete=models.CASCADE)
    is_enabled=models.BooleanField(default=False,null=True,blank=True)
    is_deleed=models.BooleanField(default=False,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    # def __str__(self):
    #     return self.notification_room_name


class Notification(models.Model):
    # x= .objects.all()
    # NotificationRoom = models.ForeignKey(NotificationRoomRoom, on_delete=models.CASCADE, null=True, blank=True, related_name="NotificationRoom")
    sender = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name='sender_messages')
    recever = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name='recever_messages')
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)


    # def __str__(self):
    #     return self.sender
