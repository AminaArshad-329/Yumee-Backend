from django.db.models import Q
from core.models import User_Profile, like_and_dislike
from chat.models import ChatRoom, All_Threads
from datetime import date, datetime, timedelta
import json
import requests
from pytz import utc


def calculate_package_expiry_date():
    all_user = list(User_Profile.objects.all())
    for users in all_user:
        current_date = date.today()
        expiry_date = users.package_date_end
        if expiry_date:
            remaining_days = (expiry_date - current_date).days
            users.remaining_days_in_exp = remaining_days
            users.save()
        else:
            print("id.{0} with username '{1}' package end date not given".format(users.id, users.your_name))
    print("Remaining Days are updated")


def package_type_change():
    all_user = list(User_Profile.objects.all())
    for users in all_user:
        remaining_days = users.remaining_days_in_exp
        if remaining_days == 0:
            users.package = ""
            users.save()
            print("id.{0} with username '{1}' package updated".format(users.id, users.your_name))
    print("Schedule Task Completed")


def calculate_age():
    now = datetime.now(utc)  # current date and time
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    birthday_profiles = User_Profile.objects.filter(date_of_birth__month=month, date_of_birth__day=day)
    for x in birthday_profiles:
        profile_birth = x.date_of_birth.strftime("%Y")
        x.age = int(year) - int(profile_birth)
        x.save()

    print("Users Age Updated")


def match_expiry_notification(**profile_data):
    # notification generator for match expiry
    url = "https://fcm.googleapis.com/fcm/send"
    payload = json.dumps({
        "to": profile_data['tokens'],
        "notification": {
            "body": "{0}{1}".format(profile_data['msg'], profile_data['user_name']),
            "OrganizationId": "2",
            "content_available": True,
            "priority": "high",
            "Title": "{}".format(profile_data['title'])
        },
        "data": {
            "priority": "high",
            "sound": "app_sound.wav",
            "content_available": True,
            "bodyText": "{}".format(profile_data['bodyText']),
            "organization": "You-Mee"
        }
    })
    headers = {
        'Authorization': 'key=AAAAxTKFuKU:APA91bEFiiTlF4IE5IC3VmLePPZUyVpMUnwXt8LwFYIXx777gSVyVnyypuy1PkbciYfeU-XS3KLJfXvf7BH_Fro-fOEWjDy6TUi7DJO6nOTDJTgWl9xsrdfVUxIbHp90drqWPyK6Fuqs',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)


def message_reply_notification(**profile_data):
    # notification generator to reply the first message
    url = "https://fcm.googleapis.com/fcm/send"
    payload = json.dumps({
        "to": profile_data['tokens'],
        "notification": {
            "body": "Le match avec {} est sur le point d'expirer ⏳ Répondez à son message".format(
                profile_data['user_name']),
            "OrganizationId": "2",
            "content_available": True,
            "priority": "high",
            "Title": "{}".format(profile_data['title'])
        },
        "data": {
            "priority": "high",
            "sound": "app_sound.wav",
            "content_available": True,
            "bodyText": "{}".format(profile_data['bodyText']),
            "organization": "You-Mee"
        }
    })
    headers = {
        'Authorization': 'key=AAAAxTKFuKU:APA91bEFiiTlF4IE5IC3VmLePPZUyVpMUnwXt8LwFYIXx777gSVyVnyypuy1PkbciYfeU-XS3KLJfXvf7BH_Fro-fOEWjDy6TUi7DJO6nOTDJTgWl9xsrdfVUxIbHp90drqWPyK6Fuqs',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)


def match_expired_notification():

    all_chat_rooms = ChatRoom.objects.select_related('user1', 'user2', 'block_by').all()
    for single_room in all_chat_rooms:
        current_time = datetime.now(utc).strftime("%m/%d/%Y, %H:%M:%S")
        chat_time = (single_room.created_at + timedelta(hours=20)).strftime("%m/%d/%Y, %H:%M:%S")
        if current_time > chat_time:
            user1_chat = single_room.Room.filter(Q(sender=single_room.user1.id, receiver=single_room.user2.id))
            user2_chat = single_room.Room.filter(Q(sender=single_room.user2.id, receiver=single_room.user1.id))
            user1_name = single_room.user1.your_name
            user1_fcm_token = single_room.user1.fcm_token
            user2_name = single_room.user2.your_name
            user2_fcm_token = single_room.user2.fcm_token
            if user1_chat and user2_chat:
                continue

            elif user1_chat or user2_chat:
                if user1_chat:
                    message_reply_notification(tokens=user2_fcm_token, user_name=user1_name,
                                               title='Reply Notification', bodyText='First Message Reply')
                else:
                    message_reply_notification(tokens=user1_fcm_token, user_name=user2_name,
                                               title='Reply Notification', bodyText='First Message Reply')

            else:
                match_expiry_notification(tokens=user2_fcm_token, user_name=user1_name,
                                          title='Match Expiry Notification', bodyText='Match Expiry',
                                          msg=" ⏲️ Ne perdez pas ce match! Envoyez le premier message à ")
                match_expiry_notification(tokens=user1_fcm_token, user_name=user2_name,
                                          title='Match Expiry Notification', bodyText='Match Expiry',
                                          msg=" ⏲️ Ne perdez pas ce match! Envoyez le premier message à ")

    print("Task: Check Match Expiry Notification Completed")


def power_like_count_change():
    all_user = list(User_Profile.objects.all())
    for users in all_user:
        if users.package == "VIP Plus" and users.power_like_count == 0:
            users.power_like_count = 1
            users.save()

    print("Power like Status Updated")


def chat_expiry_scheduler():
    chat_rooms = ChatRoom.objects.select_related('user1', 'user2', 'block_by').all()
    for single_room in chat_rooms:
        current_time = datetime.now(utc).strftime("%m/%d/%Y, %H:%M:%S")
        chat_time = (single_room.created_at + timedelta(hours=24)).strftime("%m/%d/%Y, %H:%M:%S")
        if current_time > chat_time:
            user1_chat = single_room.Room.filter(Q(sender=single_room.user1.id, receiver=single_room.user2.id))
            user2_chat = single_room.Room.filter(Q(sender=single_room.user2.id, receiver=single_room.user1.id))
            if user1_chat and user2_chat:
                continue
            else:
                # Delete all the chat of the chat room
                single_room.Room.all().delete()
                # Delete the thread related to the chat room
                All_Threads.objects.filter(room_as_thread=single_room).delete()
                from core.models import like_and_dislike
                # update the user profile active status in the like_dislike model
                like_data = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
                    .filter(Q(profile_status='Like') | Q(profile_status='Super_like'))
                user1_liked = like_data.filter(user=single_room.user1.id, is_active=True,
                                               user_profile_liked_or_dislike=single_room.user2.id) \
                    .update(is_active=False)
                user2_liked = like_data.filter(user=single_room.user2.id, is_active=True,
                                               user_profile_liked_or_dislike=single_room.user1.id) \
                    .update(is_active=False)
    print("Task Completed: Chat expiry check and move to re-kindle tab")


def delete_after_re_kindle_tab():
    chat_rooms = ChatRoom.objects.select_related('user1', 'user2', 'block_by').all()
    for single_room in chat_rooms:
        current_time = datetime.now(utc).strftime("%m/%d/%Y, %H:%M:%S")
        chat_time = (single_room.created_at + timedelta(hours=48)).strftime("%m/%d/%Y, %H:%M:%S")
        if current_time > chat_time:
            user1_chat = single_room.Room.filter(Q(sender=single_room.user1.id, receiver=single_room.user2.id))
            user2_chat = single_room.Room.filter(Q(sender=single_room.user2.id, receiver=single_room.user1.id))
            if user1_chat and user2_chat:
                continue
            else:
                like_data = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
                    .filter(Q(profile_status='Like') | Q(profile_status='Super_like'))
                user1_liked = like_data.filter(user=single_room.user1.id, is_active=False,
                                               user_profile_liked_or_dislike=single_room.user2.id).delete()
                user2_liked = like_data.filter(user=single_room.user2.id, is_active=False,
                                               user_profile_liked_or_dislike=single_room.user1.id).delete()

                # To remove matched users from eachother cross_list_user, which is used for matchs
                user1_obj = User_Profile.objects.get(id=single_room.user1.id)
                user1_cross_list = user1_obj.cross_user_list
                user2_obj = User_Profile.objects.get(id=single_room.user2.id)
                user2_cross_list = user2_obj.cross_user_list
                if str(single_room.user2.id) in user1_cross_list:
                    user1_cross_list.remove(str(single_room.user2.id))
                    user1_obj.save()
                if str(single_room.user1.id) in user2_cross_list:
                    user2_cross_list.remove(str(single_room.user1.id))
                    user2_obj.save()

                # delete the chat room at the end
                single_room.delete()

    print("Task Completed: Delete chatroom, remove likes and remove user from eachother cross_limit too")


def delete_disliked_profiles():
    """Delete disliked profiles after 7 days of every user"""

    disliked_profiled = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
        .filter(profile_status='Dislike')
    for x in disliked_profiled:
        from pytz import utc
        current_time = datetime.now(utc).strftime("%m/%d/%Y")
        liked_time = (x.created_date + timedelta(hours=48)).strftime("%m/%d/%Y")
        if current_time == liked_time:
            x.delete()
    print('Delete Disliked Profiles Scheduler Performed')
