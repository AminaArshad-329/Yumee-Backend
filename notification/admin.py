from django.contrib import admin

# Register your models here.
from .models import *
    # , Countries,Region,City

admin.site.register(Notification)
admin.site.register(NotificationRoomRoom)