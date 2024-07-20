from datetime import timezone
from re import T
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db import models
from core.models import User_Profile
import arrow as arrow
from io import BytesIO
from PIL import Image
from django.core.files import File


def compress_image(image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality=60)
    new_image = File(im_io, name=image.name)
    return new_image


def generate_file_path(instance, filename):
    now = arrow.now()
    # file will be saved to MEDIA_ROOT/chats/chatroom/images/2015/01/30/filename
    template = "chats/room_{chatroom}/images/{year}/{month:02d}/{filename}"
    return template.format(instance, year=now.year, month=now.month, filename=filename, chatroom=instance.Room)


def user_directory_path(instance, filename):
    import random
    # file will be uploaded to MEDIA_ROOT/chats/chat_room/audio/user_id_random no#_<filename>
    return 'chats/room_{2}/audio/user_{0}_{3}_{1}'.format(instance.sender.id, filename, instance.Room,
                                                          random.randint(1111, 9999))


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=100, null=True)
    user1 = models.ForeignKey(User_Profile, related_name='room_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User_Profile, related_name='room_user2', on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False, null=True, blank=True)
    is_deleed = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    block_by = models.ForeignKey(User_Profile, related_name='block_by_user', on_delete=models.CASCADE, null=True,
                                 blank=True)
    block_user = models.ForeignKey(User_Profile, related_name='user_blocked', on_delete=models.CASCADE, null=True,
                                   blank=True)

    def __str__(self):
        return self.room_name


class chat(models.Model):
    Room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True, related_name="Room")
    sender = models.ForeignKey(User_Profile, related_name='message_sender', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User_Profile, related_name='message_receiver', on_delete=models.CASCADE, null=True)
    message_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    images = models.ImageField(upload_to=generate_file_path, blank=True, null=True)
    voice_note = models.FileField(upload_to=user_directory_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.images:
            new_image = compress_image(self.images)
            self.image = new_image
        super().save(*args, **kwargs)


class All_Threads(models.Model):
    room_as_thread = models.CharField(max_length=100, null=True)
    sender = models.ForeignKey(User_Profile, related_name='messagesender', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User_Profile, related_name='messagereceiver', on_delete=models.CASCADE, null=True)
    lastMessage = models.TextField()
    lastMessage_data = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    un_seen_count = models.IntegerField(blank=True, null=True, default=0)
    un_seen_count1 = models.IntegerField(blank=True, null=True, default=0)

    # def __str__(self):
    #     return self.room_as_thread
