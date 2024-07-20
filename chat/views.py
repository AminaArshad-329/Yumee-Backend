# chat/views.py
import json
import requests

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import chat, ChatRoom, All_Threads
from chat.serializers import ChatSerializer, ChatRoomSerializer, ThreadSerializer, ChatListSerializer, \
    ThreadSerializerData
from core.models import User_Profile
from core.serializers import ProfilePostSerializer, UserChatProfileSerializer


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_id):
    return render(request, 'chat/room.html', {
        'room_id': room_id
    })


class ChatRoomInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            user1 = User_Profile.objects.filter(user=request.user.id).values_list('id', flat=True).first()
            user2 = request.data['user2']
            q1 = Q(user1=user1, user2=user2)
            q2 = Q(user1=user2, user2=user1)
            query = q1 | q2
            if ChatRoom.objects.filter(query, is_enabled=True).exists():
                room = ChatRoom.objects.get(query, is_enabled=True)
                room_serializer = ChatRoomSerializer(room, context={'request': request})
                return Response({'message': 'Chat Enabled', "chat_room": room_serializer.data})
            else:
                return Response({'message': 'Chat Not Enabled'})
        except Exception as e:
            return Response({'message': 'Chat Not Enabled', 'error': str(e)})


class ChatList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # manage_read_receipts
        room = request.data.dict()
        room = room.get('room_name')
        login_user = User_Profile.objects.filter(user=request.user).values_list('user', flat=True).first()
        reve = chat.objects.filter(Room__room_name=room, receiver__user=login_user).values_list('receiver__user',
                                                                                                flat=True).first()
        manage_read = User_Profile.objects.filter(user=reve).values_list('manage_read_receipts', flat=True).first()
        if manage_read == True:
            if login_user == reve:
                chat.objects.filter(Room__room_name=room, receiver__user=login_user).update(is_seen=True)
            else:
                pass
        chat_room_id = chat.objects.filter(Room__room_name=room).order_by('-created_at')
        serializer = ChatListSerializer(chat_room_id, many=True, context={'request': request})
        status_is_enabled = ChatRoom.objects.filter(room_name=room).values_list('is_enabled', flat=True).first()
        block_by = ChatRoom.objects.filter(room_name=room).values_list('block_by', flat=True).first()
        user1 = ChatRoom.objects.filter(room_name=room).values_list('user1', flat=True).first()
        user2 = ChatRoom.objects.filter(room_name=room).values_list('user2', flat=True).first()
        if block_by:
            if block_by == user1:
                block_to_id = user2
            else:
                block_to_id = user1
            return Response(
                {"status_is_enabled": status_is_enabled, "chat_messages": serializer.data, "block_to": block_to_id},
                status=status.HTTP_200_OK)
        else:
            return Response(
                {"status_is_enabled": status_is_enabled, "chat_messages": serializer.data},
                status=status.HTTP_200_OK)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def message_notification(self, **profile_data):
        url = "https://fcm.googleapis.com/fcm/send"
        payload = json.dumps({
            "to": profile_data['tokens'],
            "notification": {
                # "body": "You got match with by " + profile_data['user_name'],
                "body": "{1}{0}".format(profile_data['msg'], profile_data['user_name']),
                "OrganizationId": "2",
                "content_available": True,
                "priority": "high",
                "Title": "{}".format(profile_data['title'])
            },
            "data": {
                "priority": "high",
                "sound": "app_sound.wav",
                "content_available": True,
                "bodyText": "Chat",
                "senderID": profile_data['sender_id'], "room_id": profile_data['room'],
                "senderData": profile_data['senderData'],
                "organization": "You-Mee"
            }
        })
        headers = {
            'Authorization': 'key=AAAAxTKFuKU:APA91bEFiiTlF4IE5IC3VmLePPZUyVpMUnwXt8LwFYIXx777gSVyVnyypuy1PkbciYfeU-XS3KLJfXvf7BH_Fro-fOEWjDy6TUi7DJO6nOTDJTgWl9xsrdfVUxIbHp90drqWPyK6Fuqs',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

    def post(self, request):
        chat_data = request.data.copy()
        user = User_Profile.objects.filter(user=request.user.id).values_list('id', flat=True).first()
        room = ChatRoom.objects.filter \
            (Q(user1=user, user2=request.data['receiver'], is_enabled=True) | Q(user1=request.data['receiver'],
                                                                                user2=user, is_enabled=True)) \
            .values_list("id", flat=True).first()
        if not room:
            return Response({"Message": "Blocked"}, status=status.HTTP_200_OK)
        chat_data.update({'Room': room, "sender": user})
        serializer = ChatSerializer(data=chat_data)
        if serializer.is_valid():
            serializer.save()
            room_name = ChatRoom.objects.filter(id=room).values_list('room_name', flat=True).first()
            room_id = room
            threads = All_Threads.objects.filter(room_as_thread=room_name)  # .values_list('room_as_thread', flat=True)
            if threads:
                updated_last_message = chat.objects.filter(Room=room_id).values_list('message_text', flat=True).last()
                date = chat.objects.filter(Room=room_id, message_text=updated_last_message).values_list('created_at',
                                                                                                        flat=True).last()
                counter = chat.objects.filter(is_seen=False, Room=room_id, receiver=request.data['receiver']).count()
                counter1 = chat.objects.filter(is_seen=False, Room=room_id, sender=user).count()
                All_Threads.objects.filter(room_as_thread=room_name).update(lastMessage=updated_last_message,
                                                                            lastMessage_data=date, un_seen_count=counter
                                                                            , un_seen_count1=counter1, sender=user,
                                                                            receiver=request.data['receiver'])
                last_message_thread = All_Threads.objects.filter(room_as_thread=room_name)
                serializer = ThreadSerializer(last_message_thread, many=True, context={'request': request})
            else:
                # Creating thread
                message = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values(
                    'message_text').exists()) or \
                          (chat.objects.filter(sender=request.data['receiver'], receiver=user).values(
                              'message_text').exists())
                if message == True:
                    updated_last_message = chat.objects.filter(Room=room_id).values_list('message_text',
                                                                                         flat=True).last()
                    date = chat.objects.filter(Room=room_id, message_text=updated_last_message).values_list(
                        'created_at', flat=True).last()
                    counter = chat.objects.filter(is_seen=False, Room=room_id,
                                                  receiver=request.data['receiver']).count()
                    counter1 = chat.objects.filter(is_seen=False, Room=room_id, sender=user).count()
                    All_Threads.objects.filter(room_as_thread=room_name).update(un_seen_count=counter)
                    All_Threads.objects.filter(room_as_thread=room_name).update(un_seen_count1=counter1)
                    chat_room_name = (ChatRoom.objects.filter(user1=user, user2=request.data['receiver']).values_list(
                        "room_name", flat=True).first()) or \
                                     (ChatRoom.objects.filter(user1=request.data['receiver'], user2=user).values_list(
                                         "room_name", flat=True).first())
                    serializer = ThreadSerializerData(
                        data={"room_as_thread": chat_room_name, 'sender': user, 'receiver': request.data['receiver'],
                              'lastMessage': updated_last_message, 'lastMessage_data ': date, },
                        context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        print(serializer.errors)
                else:
                    pass
                date = chat.objects.filter(Room=room_id, message_text=updated_last_message).values_list('created_at',
                                                                                                        flat=True).last()
                All_Threads.objects.filter(room_as_thread=room_name).update(lastMessage_data=date)
                last_message_thread = All_Threads.objects.filter(room_as_thread=room_name)
                serializer = ThreadSerializer(last_message_thread, many=True, context={'request': request})
            created = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values_list('created_at',
                                                                                                       flat=True).last()) or \
                      (chat.objects.filter(sender=request.data['receiver'], receiver=user).values_list('created_at',
                                                                                                       flat=True).last())

            modified = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values_list('modified_at',
                                                                                                        flat=True).last()) or \
                       (chat.objects.filter(sender=request.data['receiver'], receiver=user).values_list('modified_at',
                                                                                                        flat=True).last())
            message = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values_list(
                'message_text', flat=True).last()) or \
                      (chat.objects.filter(sender=request.data['receiver'], receiver=user).values_list(
                          'images', flat=True).last())

            image = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values_list(
                'images', flat=True).last()) or \
                    (chat.objects.filter(sender=request.data['receiver'], receiver=user).values_list(
                        'images', flat=True).last())

            voice_note = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values_list(
                'voice_note', flat=True).last()) or \
                         (chat.objects.filter(sender=request.data['receiver'], receiver=user).values_list(
                             'voice_note', flat=True).last())
            try:
                message_obj = (chat.objects.filter(sender=user, receiver=request.data['receiver']).values('id', 'Room',
                                                                                                          'Room__room_name',
                                                                                                          'is_seen',
                                                                                                          'is_delete',
                                                                                                          'receiver',
                                                                                                          'sender').last())
                user1 = User_Profile.objects.filter(id=user)  # .values_list('id', flat=True).first()
                serializers = ProfilePostSerializer(user1, many=True, context={'request': request})
                data1 = serializers.data
                data1 = json.loads(json.dumps(data1))
                data1 = data1[0]
                sender_pic = data1['user_profile_pic']
                user2 = User_Profile.objects.filter(
                    id=request.data['receiver'])  # .values_list('id', flat=True).first()
                serializers = ProfilePostSerializer(user2, many=True, context={'request': request})
                ab = serializers.data
                ab = json.loads(json.dumps(ab))
                ab = ab[0]
                receiver_pic = ab['user_profile_pic']
            except:
                message_obj = (
                    chat.objects.filter(sender=request.data['receiver'], receiver=user).values('id', 'Room', 'is_seen',
                                                                                               'is_delete', 'receiver',
                                                                                               'sender').last())
                user1 = User_Profile.objects.filter(
                    id=request.data['receiver'])  # .values_list('id', flat=True).first()
                serializers = ProfilePostSerializer(user1, many=True, context={'request': request})
                data1 = serializers.data
                data1 = json.loads(json.dumps(data1))
                data1 = data1[0]
                sender_pic = data1['user_profile_pic']

                user2 = User_Profile.objects.filter(
                    id=request.data['receiver'])  # .values_list('id', flat=True).first()
                serializers = ProfilePostSerializer(user2, many=True, context={'request': request})
                ab = serializers.data
                ab = json.loads(json.dumps(ab))
                ab = ab[0]
                receiver_pic = ab['user_profile_pic']

            message_obj["type"] = "chat_message"
            message_obj["created_at"] = str(created)
            message_obj["modified_at"] = str(modified)
            from django.conf import settings
            if image:
                message_obj['image'] = 'https://ng-dating-app.s3.us-east-2.amazonaws.com/%s' % image
                message_obj['message'] = None
            elif voice_note:
                message_obj['voice_note'] = 'https://ng-dating-app.s3.us-east-2.amazonaws.com/%s' % voice_note
            else:
                message_obj['message'] = message
            message_obj['picture_sender'] = sender_pic
            message_obj['picture_receiver'] = receiver_pic

            layer = get_channel_layer()
            chat_room_name = (ChatRoom.objects.filter(user1=user, user2=request.data['receiver']).values_list(
                "room_name", flat=True).first()) or \
                             (ChatRoom.objects.filter(user1=request.data['receiver'], user2=user).values_list(
                                 "room_name", flat=True).first())
            async_to_sync(layer.group_send)(str(chat_room_name), message_obj)
            async_to_sync(layer.group_send)(str("allrooms"), message_obj)
            sender_data = User_Profile.objects.get(user=request.user)
            receiver_data = User_Profile.objects.get(id=request.data['receiver'])
            sender_profile_data = User_Profile.objects.filter(user=request.user)
            sender_serializers = UserChatProfileSerializer(sender_profile_data, many=True, context={'request': request})
            self.message_notification(tokens=receiver_data.fcm_token, user_name=sender_data.your_name,
                                      title='Message Notification', sender_id=sender_data.id,
                                      msg=" Vous avez un message de ", room=room_name,
                                      senderData=sender_serializers.data)
            return Response(
                {"message": "Message Sent Successfully", "threads_data": serializer.data, "room_name": room_name},
                status=status.HTTP_200_OK)
        else:
            return Response({"Message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message = chat.objects.get(id=request.data['id'], is_delete=False)
            serializer = ChatSerializer(instance=message, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
            return Response({"message": serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"Message": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteChat(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        # transformer = self.get_object(pk)
        transformer = chat.objects.get(id=pk, is_delete=False)
        transformer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_room_id = self.request.data['chat_room']
        room_get = ChatRoom.objects.get(room_name=chat_room_id)
        user1_chat = room_get.Room.filter(Q(sender=room_get.user1.id, receiver=room_get.user2.id))
        user2_chat = room_get.Room.filter(Q(sender=room_get.user2.id, receiver=room_get.user1.id))
        if user1_chat and user2_chat:
            return Response({'chat_status_check': True}, status=status.HTTP_200_OK)
        else:
            return Response({'chat_status_check': False}, status=status.HTTP_200_OK)


class ThreadList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User_Profile.objects.filter(user=request.user.id).values_list('id', flat=True).first()
        list__a = (All_Threads.objects.filter(sender=user).values_list('room_as_thread', flat=True)).all()
        list__b = (All_Threads.objects.filter(receiver=user).values_list('room_as_thread', flat=True)).all()
        list__a = list(list__a)
        list__b = list(list__b)
        room_list = list__a + list__b
        for x in room_list:
            counter = chat.objects.filter(is_seen=False, Room__room_name=x, receiver=user).count()
            counter1 = chat.objects.filter(is_seen=False, Room__room_name=x, sender=user).count()
            All_Threads.objects.filter(room_as_thread=x).update(un_seen_count=counter)
            All_Threads.objects.filter(room_as_thread=x).update(un_seen_count1=counter1)

        list_a = (All_Threads.objects.filter(sender=user).order_by('-modified_at'))
        list_b = (All_Threads.objects.filter(receiver=user).order_by('-modified_at'))
        list_of_thread = list_a.union(list_b)
        serializer = ThreadSerializer(list_of_thread, many=True, context={'request': request})
        return Response({"All_ThreadList": serializer.data}, status=status.HTTP_200_OK)


class BlockMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        block_user_id = request.data['id']
        user_status = request.data['is_enabled']
        user_obj = User_Profile.objects.filter(user=request.user).values_list('id', flat=True).first()
        room = (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj).values_list('room_name',
                                                                                         flat=True)).first() or \
               (ChatRoom.objects.filter(user1=block_user_id, user2=user_obj).values_list('room_name',
                                                                                         flat=True)).first()
        blocker_id = (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj).values_list('block_by',
                                                                                               flat=True)).first() or \
                     (ChatRoom.objects.filter(user1=block_user_id, user2=user_obj).values_list('block_by',
                                                                                               flat=True)).first()
        if user_status == "True" or user_status == "true":
            if blocker_id is None:
                (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj, room_name=room).update(block_by=None,
                                                                                                     block_user=None,
                                                                                                     is_enabled=user_status.capitalize())) or (
                    ChatRoom.objects.filter(user1=block_user_id, user2=user_obj, room_name=room).update(block_by=None,
                                                                                                        block_user=None,
                                                                                                        is_enabled=user_status.capitalize()))
                return Response({"Message": "Profile Successfully Updated", "Blocked_user": block_user_id},
                                status=status.HTTP_200_OK)
            else:
                if user_obj == blocker_id:
                    (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj, room_name=room).update(block_by=None,
                                                                                                         block_user=None,
                                                                                                         is_enabled=user_status.capitalize())) or (
                        ChatRoom.objects.filter(user1=block_user_id, user2=user_obj, room_name=room).update(
                            block_by=None, block_user=None, is_enabled=user_status.capitalize()))
                    return Response({"Message": "Profile Successfully Updated", "Blocked_user": block_user_id},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"Message": "You can't unblock this user", "Blocked_user": block_user_id},
                                    status=status.HTTP_200_OK)
        else:
            value = ((ChatRoom.objects.filter(room_name=room).values_list('is_enabled', flat=True).first()))
            if (value == False) or (value == "False"):
                return Response({"Message": "Already unblock this user", "Blocked_user": block_user_id},
                                status=status.HTTP_200_OK)
            else:
                statuss = request.data['is_enabled']
                statuss = statuss.capitalize()
                statuss = statuss
                if statuss == "False":
                    (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj, room_name=room).update(
                        block_by=user_obj, is_enabled=statuss, block_user=request.data['id'])) or \
                    (ChatRoom.objects.filter(user1=block_user_id, user2=user_obj, room_name=room).update(
                        block_by=user_obj, is_enabled=statuss, block_user=request.data['id']))
                else:
                    (ChatRoom.objects.filter(user2=block_user_id, user1=user_obj, room_name=room).update(block_by=None,
                                                                                                         block_user=request.data['id'],
                                                                                                         is_enabled=statuss)) or \
                    (ChatRoom.objects.filter(user1=block_user_id, user2=user_obj, room_name=room).update(block_by=None,
                                                                                                         block_user=request.data['id'],
                                                                                                         is_enabled=statuss))
                return Response({"Message": "Profile Successfully Updated", "Blocked_user": block_user_id},
                                status=status.HTTP_200_OK)


class SendMessageSeen(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = User_Profile.objects.filter(user=self.request.user).get().id
        chat_room_data = ChatRoom.objects.filter(room_name=request.data['chat_room'])
        if chat_room_data:
            room_name = ChatRoom.objects.get(room_name=request.data['chat_room'])
            update_method = room_name.Room.filter(receiver=receiver_id, is_seen=False).update(is_seen=True)
            chat_sender = room_name.Room.values_list('sender', flat=True).exclude(sender=receiver_id)[:1]
            sender_status = User_Profile.objects.filter(id=chat_sender).values('id', 'manage_read_receipts').first()
            print(sender_status)
            sender_status["type"] = "message_seen_status"
            layer = get_channel_layer()

            async_to_sync(layer.group_send)(str(room_name), sender_status)
            # async_to_sync(layer.group_send)(str("allrooms"), sender_status)
            return Response({"message": "message seen successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Chat_room Not Found"}, status=status.HTTP_400_BAD_REQUEST)
