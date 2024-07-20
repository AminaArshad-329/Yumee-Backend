# notification/views.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from core.models import User_Profile
from notification.models import Notification, NotificationRoomRoom
from notification.serializers import NotificationSerializer, NotificationRoomSerializer, NotificationListSerializer
from core.serializers import ProfilePostSerializer


def index(request):
    # id = Notification.objects.values("recever").first()
    # print(id,"/////////////")
    # return render(request, 'notification/index.html',{"recever": id.get("recever")})
    return render(request, 'notification/index.html')

def room(request, user_id):
    return render(request, 'notification/room.html', {
        'user_id': user_id
    })

class NotificationRoomInfo(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            user1 = User_Profile.objects.filter(user = request.user.id).values_list('id', flat=True).first()
            user2=request.data['user2']
            print(type(user2))
            q1=Q(user1=user1,user2=user2)
            q2=Q(user1=user2,user2=user1)
            print(q1,"/////////////",q2)
            query=q1 | q2
            if NotificationRoomRoom.objects.filter(query,is_enabled=True).exists():
                print("???????")
                room=NotificationRoomRoom.objects.get(query, is_enabled=True)
                print(room)
                room_serializer=NotificationRoomSerializer(room)
                return Response({'message':'Notification Enabled',"Notification_room":room_serializer.data})
            else:
                return Response({'message': 'Notification Not Enabled'})
        except Exception as e:
            return Response({'message': 'Notification Not Enabled', 'error':str(e)})


# class NotificationList(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         try:
#             notifications = Notification.objects.filter(recever=request.user,is_delete=False)
#             serializer = NotificationSerializer(notifications, many=True)
#             # print(serializer.data)
#             return Response({"data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"detail": "Something went wrong!", "Error": str(e)}, status=status.HTTP_409_CONFLICT)
class NotificationList(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # manage_read_receipts

        login_user = User_Profile.objects.filter(user = request.user).values_list('id', flat=True).first()
        print(login_user, "????/")
        reve = Notification.objects.filter(recever__id = login_user).values_list('recever__id', flat=True).first()
        print(reve)
        # manage_read = User_Profile.objects.filter(user=reve).values_list('manage_read_receipts', flat=True).first()
        # print(manage_read)
        # room = dict(room._iterlists())
        # print(room,"////?")
        notification_room_id = Notification.objects.filter(recever__id = login_user).order_by('created_date').exclude(is_seen=True)
        print(notification_room_id,"???????????/")
            # allchat = chat.objects.filter(Room_id=chat_room_id,is_delete=False)
            # # allchat = chat.objects.filter(Room_id=chat_room_id,is_delete=False)

        serializer = NotificationListSerializer(notification_room_id, many=True)
        print(serializer.data)
        if login_user == reve:
            print("if")
            Notification.objects.filter(recever__id = login_user).update(is_seen= True)
            print("if end")
        return Response({"notification_messages": serializer.data}, status=status.HTTP_200_OK)



class SingleNotification(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request, pk):
        try:
            notification = Notification.objects.get(id = pk,recever=request.user,is_delete=False)
            serializer = NotificationSerializer(notification, many=False)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Something went wrong!", "Error": str(e)}, status=status.HTTP_409_CONFLICT)


class SendNotification(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            a= request.user.id
            a = User_Profile.objects.filter(user= a).values_list("id",flat=True).first()
            print(a)
            user = User_Profile.objects.filter(user=request.user)
            sender_serializer = ProfilePostSerializer(user, many= True)
            user_profile= sender_serializer.data

            # serializer = NotificationSerializer(data=request.data)
            serializer = NotificationSerializer(data={"sender":a, "recever": request.data['recever'], "text":  request.data['text']}, partial=True)
            # print(serializer.data)
            if serializer.is_valid():
                print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                serializer=serializer.save()
            else:
                print("Invalid")
                print(serializer.errors)
            receiver_id=request.data['recever']
            notification_dic = {"message": request.data['text'],"recever":receiver_id,"seen":False,"is_deleted":False, "sender":user_profile}
            notification_dic["type"] = "notification"
            layer = get_channel_layer()
            async_to_sync(layer.group_send)('user_notification_' + str(receiver_id), notification_dic)

            return Response({"message": "Notification Sent Successfully"} , status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Something went wrong!", "Error": str(e)}, status=status.HTTP_409_CONFLICT)

class UpdateDeleteNotification(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            notification = Notification.objects.get(id = request.data['id'],is_delete=False)
            serializer = NotificationSerializer(instance=notification, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
            print(serializer.data)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Something went wrong!", "Error": str(e)}, status=status.HTTP_409_CONFLICT)
