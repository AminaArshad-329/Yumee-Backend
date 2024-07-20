from django.contrib import admin

# Register your models here.
from .models import chat, ChatRoom, All_Threads


class ChatData(admin.ModelAdmin):
    list_display = ['id', 'Room', 'sender', 'receiver', 'is_delete', 'is_seen']

    class Meta:
        model = chat
        fields = '__all__'


class ThreadsData(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'un_seen_count', 'un_seen_count1']

    class Meta:
        model = All_Threads
        fields = '__all__'


class ChatRoomData(admin.ModelAdmin):
    list_display = ['id', 'room_name', 'user1', 'user2', 'is_enabled', 'block_by', 'created_at', 'modified_at']

    class Meta:
        model = ChatRoom
        fields = '__all__'


admin.site.register(chat, ChatData)
admin.site.register(ChatRoom, ChatRoomData)
admin.site.register(All_Threads, ThreadsData)
