import random
import string
from datetime import timedelta, date
from rest_framework.decorators import api_view

import geopy as geopy
import geopy.distance
import requests
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone
from google.auth.transport._http_client import Response
from pylint.checkers.typecheck import _
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
# Generate Jwt-Token
from rest_framework_jwt.settings import api_settings
from core.models import *
# from env.Scripts.odf2xhtml import usage
from .core_functions import generateOTP, twilio_otp, otp_verification_check, Pagination, \
    qdict_to_dict
from .serializers import *

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from password_strength import PasswordPolicy, PasswordStats
from datetime import datetime
from chat.serializers import ChatRoomSerializer
from chat.models import *
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=2,  # need min. 2 digits
    special=2,  # need min. 2 special characters
    nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
)

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=2,  # need min. 2 digits
    special=2,  # need min. 2 special characters
    nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
)


# =========================Function start
def email_sending(key, template, email, msg):
    context = {'template': template, 'url': key}
    message = get_template(context['template']).render(context['url'])
    email = EmailMessage(msg, message, to=[email])
    email.content_subtype = 'html'
    email.send()


def password_strenght(password):
    stats = PasswordStats(password)
    strenght = stats.strength()
    return strenght


def isNum(data):
    try:
        int(data)
        return True
    except ValueError:
        return False


def set_if_not_none(mapping, key, value):
    if value is not None:
        mapping[key] = value


# def get_jwt_token(user):
#
#     payload = jwt_payload_handler(user)
#     token = jwt_encode_handler(payload)
#     if UserToken.objects.filter(token=token, user=user).exists():
#         pass
#     else:
#         UserToken.objects.create(token=token, user=user, expireAT=timezone.now() + timezone.timedelta(days=7))
#     emp=EmployeeProfile.objects.get(user__user=user)
#     emp.online = True
#     emp.online_status = timezone.now()
#     emp.save(update_fields=['online'])
#     return token

# ================================Views Start
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def payment_success(request):
    return Response(template_name='payment.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def payment_fail(request):
    return Response(template_name='payment_fail.html')


class User_Profiles(viewsets.ViewSet):  # User class

    @action(detail=False, methods=['post'])
    def user_login(self, request):
        username = request.data["email"]
        temp = isNum(username)
        if temp == True:
            password = 'Abdsviueenweskl'
        else:
            password = request.data["password"]

        if User.objects.filter(username=username).exists():
            object_user = User.objects.get(username=username)
            user_profile_object = User_Profile.objects.get(user=object_user.id)
            if user_profile_object.is_banned:
                if request.data['lang'] == 'fr':
                    return Response({"error": "Vous êtes temporairement banni de l'application"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "You are temporarily banned from the app"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # newapi = 'http://3.13.18.134/core/login/'    old IP
                newapi = 'http://18.221.70.79/core/login/'
                data1 = {"username": object_user.username,
                         "password": password}
                all_object = User_Profile.objects.filter(user=object_user.id)
                serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
                response = requests.post(newapi, data=data1).json()
                if 'token' in response:
                    key = response['token']
                    return Response({"Token": key, "Role": user_profile_object.role, "user_object": serializer.data, },
                                    status=status.HTTP_200_OK)

                else:
                    return Response({"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            temp = isNum(username)
            if temp == True:
                return Response({"Message": "Phone Number does not Exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Email does not Exist"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'patch'])
    def signup(self, request):  # user_login
        if request.method == "POST":
            if User.objects.filter(Q(username=request.data['email'])).exists():
                return Response({"message": "Already Registered"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if password_strenght(request.data['password']) > 0.22:

                    user = User.objects.create_user(
                        username=request.data['email'],
                        password=request.data['password']

                    )
                    if user != '':
                        email = request.data['email']
                        user = User.objects.get(username=email)
                        otp = {
                            "otp": generateOTP()
                        }
                        current_date = date.today().isoformat()
                        expiry_date = (date.today() + timedelta(days=1)).isoformat()
                        serializer = ProfilePostUserSerializer(
                            data={"user": user.id, "otp": otp['otp'], "registration_status": False,
                                  'email': request.data['email'], 'package': 'VIP Plus',
                                  'package_duration': '15 Days Trial',
                                  'package_date_start': current_date,
                                  'package_date_end': expiry_date})
                        if serializer.is_valid():
                            serializer.save()
                            if request.data['lang'] == 'fr':
                                email_sending(otp, 'Activation_Email_fr.html', email, 'Email Confirmation')
                            else:
                                email_sending(otp, 'Activation_Email.html', email, 'Email Confirmation')
                            all_object = User_Profile.objects.filter(user=user)
                            serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
                            return Response({"Successfully_Profile_Created": serializer.data},
                                            status=status.HTTP_201_CREATED)
                        else:
                            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({'Message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"Message": "Weak password"}, status=status.HTTP_411_LENGTH_REQUIRED)

        if request.method == "PATCH":  # Update User profile
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            profile_obj = request.data
            profile_img = request.FILES

            serializer = ProfilePostSerializer(user_obj, data=profile_obj, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                all_object = User_Profile.objects.filter(user=user_obj)
                serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
                return Response({"Update_Profile_Successfully": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def delete_picture(self, request):
        try:
            #       user_obj = User.objects.get(id=request.user.id)
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        dic = request.data
        id = dic["id"]
        instance = User_Picture.objects.get(user_profile=user_obj, id=id)
        if instance:
            instance.delete()
            user_obj = User.objects.get(id=request.user.id)
            all_object = User_Profile.objects.filter(user=user_obj)
            serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})

            return Response({"Profile_Picture_Successfully_Delete": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "This Picture does not exist"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'])
    def update_picture(self, request):
        try:
            user_obj = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        profile_obj = request.data
        profile_img = request.FILES
        serializer = PicturePostSerializer(user_obj, data=profile_obj, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            all_object = User_Profile.objects.filter(user=user_obj)
            serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
            return Response({"Update_Picture_Successfully": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes((IsAuthenticated,))
    @action(detail=False, methods=['put', 'post'])
    def otp(self, request):
        if request.method == "PUT":  # Resend OTP
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                if "email" in request.data and User.objects.filter(username=request.data['email']).exists():
                    user_obj = User.objects.get(username=request.data['email'])
                else:
                    return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            if user_obj != '':
                user = User_Profile.objects.get(user=user_obj)
                otp = {
                    "otp": generateOTP()
                }
                serializer = ResendOtpSerializer(user, data={"otp": otp['otp']}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    if request.data['lang'] == 'fr':
                        email_sending(otp, 'Activation_Email_fr.html', user, 'Email Confirmation')
                    else:
                        email_sending(otp, 'Activation_Email.html', user, 'Email Confirmation')
                    return Response({'Message': 'Resend OTP Successfully!'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


            else:
                return Response({'Message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "POST":  # Check OTP and Activate Account
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                if "email" in request.data and User.objects.filter(username=request.data['email']).exists():
                    user_obj = User.objects.get(username=request.data['email'])
                else:
                    return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            otp_object = User_Profile.objects.get(user=user_obj)
            naive = otp_object.otp_time

            now_utc = datetime.now(timezone.utc)
            subtract_date = (now_utc - naive)
            minutes = (subtract_date.seconds // 60) % 60
            if minutes >= 10:
                return Response({'Message': "OTP Expired! "}, status=status.HTTP_408_REQUEST_TIMEOUT)
            otp = request.data['otp']
            if otp == otp_object.otp:
                serializer = ResendOtpSerializer(otp_object, data={"verfication_status": True}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'Message': "Account Verified!"}, status=status.HTTP_200_OK)
                else:
                    return Response({'Error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': "Enter correct OTP code"}, status=status.HTTP_400_BAD_REQUEST)

    #
    # {
    #     "phone_number": "03356105885",
    #     "password": "MMMirza@1213AAA"
    # }

    @action(detail=False, methods=['post', 'put'])
    def signup_phone(self, request):  # user_login
        if request.method == "POST":
            if User.objects.filter(Q(username=request.data['phone_number'])).exists():
                phone = request.data['phone_number']
                # user = User.objects.get(username=phone)
                user_obj = User.objects.get(username=request.data['phone_number'])
                user_profile_object = User_Profile.objects.get(user=user_obj.id)
                twilio_otp(request.data['phone_number'])
                return Response({"Already_Register": "True", "Role": user_profile_object.role,
                                 "Verfication_Status": user_profile_object.verfication_status,
                                 "Registration_Status": user_profile_object.registration_status},
                                status=status.HTTP_200_OK)
            else:
                user = User.objects.create_user(username=request.data['phone_number'], password='Abdsviueenweskl')
                if user != '':
                    phone = request.data['phone_number']
                    user = User.objects.get(username=phone)
                    serializer = ProfilePostUserSerializer(data={"user": user.id, "registration_status": False})
                    if serializer.is_valid():
                        serializer.save()
                        twilio_otp(request.data['phone_number'])
                        return Response({"Already_Register": "False", 'Message': 'Successfully Create and OTP Send'},
                                        status.HTTP_200_OK)
                    else:
                        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "PUT":  # Update User profile
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            profile_obj = request.data
            serializer = ProfilePostSerializer(user_obj, data=profile_obj, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response({'Message': 'Update Profile Successfully!'}, status.HTTP_200_OK)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post', 'put'])
    def twilio_otp(self, request):  # user_login
        if request.method == "POST":  # verify OTP
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                if "email" in request.data and User.objects.filter(username=request.data['email']).exists():
                    user_obj = User.objects.get(username=request.data['email'])
                else:
                    return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            otp_object = User_Profile.objects.get(user=user_obj)
            sender_phone = user_obj.username
            otp = request.data['otp']
            if otp_verification_check(sender_phone, otp) == True:
                serializer = ResendOtpSerializer(otp_object, data={"verfication_status": True}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {'Message': "Account Verified!", "Verfication_Status": otp_object.verfication_status,
                         "Registration_Status": otp_object.registration_status}, status=status.HTTP_200_OK)
                else:
                    return Response({'Error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': "Enter correct OTP code"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "PUT":  # Resend OTP
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                if "email" in request.data and User.objects.filter(username=request.data['email']).exists():
                    user_obj = User.objects.get(username=request.data['email'])
                else:
                    return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            if user_obj != '':
                user = User_Profile.objects.get(user=user_obj)
                send_number = user.user.username
                twilio_otp(send_number)
                return Response({'Message': 'Resend OTP Successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'Message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):  # user_profile_update
        package_days = {'1 Month': 30, '3 Month': 91, '6 Month': 182, '15 Days Trial': 15}
        if request.method == "PATCH":  # Update User profile
            try:
                user_obj = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            profile_obj = request.data.copy()
            if 'package' in profile_obj:  # for packge start data and end date updation
                package_time = request.data.get('package_duration')
                current_date = date.today().isoformat()
                x = package_days.get(package_time)
                expiry_date = (date.today() + timedelta(days=int(x))).isoformat()
                profile_obj.update({'package_date_start': current_date, 'package_date_end': expiry_date})
            serializer = ProfileUpdateSerializer(user_obj, data=profile_obj, partial=True)
            if serializer.is_valid():
                serializer.save()
                all_object = User_Profile.objects.filter(user=user_obj)
                serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
                return Response({"Successfully_Profile_Updated_Data": serializer.data}, status=status.HTTP_200_OK)

            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        try:
            # user = User.objects.get(id=request.user.id)
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user_obj.delete()
        user = User.objects.get(username=request.user)
        user.delete()
        return Response({"Message": "User_Profile_Successfully_Delete"})

    @action(detail=False, methods=['post'])
    def logout_account(self, request):
        try:
            # user = User.objects.get(id=request.user.id)
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        User_Profile.objects.filter(user=request.user).update(fcm_token=None)
        return Response({"Message": "User_Profile_Successfully_Logout"})

    @action(detail=False, methods=['get'])
    def user_banned_status(self, request):
        try:
            banned_status = User_Profile.objects.get(user=request.user)
            return Response({'banned_status': banned_status.is_banned}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'No Such User'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def user_profile_data(self, request):
        user_id = User_Profile.objects.filter(user=self.request.user)
        serializer = ProfilePostSerializer(user_id, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class password(viewsets.ViewSet):  # User class
    @action(detail=False, methods=['post'])
    def forget_password(self, request):  # forget pass email
        email = request.data['email']
        temp = isNum(email)
        if temp == False:
            if (User.objects.filter(username=email).exists()):
                user = User.objects.get(username=email)
                user = User_Profile.objects.get(user=user)
                if user != '':
                    otp = {
                        "otp": generateOTP()
                    }
                    serializer = ResendOtpSerializer(user, data={"otp": otp['otp']}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        if request.data['lang'] == 'fr':
                            email_sending(otp, 'Activation_Email_fr.html', email, 'Forget Password')
                        else:
                            email_sending(otp, 'Activation_Email.html', email, 'Forget Password')
                        return Response({'Message': 'OTP Send Successfully!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'Message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"msg": "Not valid Email"}, status=status.HTTP_404_NOT_FOUND)
        if temp == True:
            if User.objects.filter(username=email).exists():
                user = User.objects.get(username=email)
                twilio_otp(user)
                return Response({'Message': 'OTP Send Successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Number is not Register"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put'])
    def reset_password(self, request):

        password1 = request.data['password1']
        password2 = request.data['password2']
        if password1 == password2:
            password = password2

            if password_strenght(password) > 0.22:

                user_obj = User.objects.get(username=request.data['email'])
                if user_obj.check_password(password) == True:
                    return Response({'Message': 'New and Current Password cannot be same.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    change_pass = User.objects.get(pk=user_obj.id)
                    change_pass.set_password(password)
                    change_pass.save()

                    return Response({'Message': 'Successfully update'}, status=status.HTTP_200_OK)

            return Response({"Message": "Weak password"}, status=status.HTTP_411_LENGTH_REQUIRED)
        else:
            return Response({'Message': 'password_mismatch'}, status=status.HTTP_400_BAD_REQUEST)


class homescreen(viewsets.ViewSet):  # Homescreen class
    @action(detail=False, methods=['post'])
    def homescreen_profile(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if user_obj != '':
            interested = user_obj.interested_in
            city = user_obj.city
            interested_age = user_obj.interested_age
            max_interested_age = user_obj.max_interested_age
            user_distance = user_obj.distance
            if user_distance:
                user_coords = User_Profile.objects.filter(user=request.user).values('latitude', 'longitude')[0]
                all_user_coords = User_Profile.objects.all().values('latitude', 'longitude', 'user')
                x, y = user_coords.get('latitude'), user_coords.get('longitude')
                all_fillter_user_id = []
                for i in all_user_coords:
                    coords_2 = (i.get('latitude'), i.get('longitude'))
                    coords_1 = (x, y)
                    distance = geopy.distance.distance(coords_1, coords_2).km
                    if distance <= user_distance:
                        fillter_user_id = i.get('user')
                        all_fillter_user_id.append(fillter_user_id)
                if interested == 'editprofile_gender_checkboxboth' and interested_age and max_interested_age:
                    all_object = User_Profile.objects.filter(age__range=(interested_age, max_interested_age),
                                                             is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman',
                                                        interested_in='editprofile_gender_checkboxwoman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman',
                                                        interested_in='editprofile_gender_checkboxman')
                elif interested == 'editprofile_gender_checkboxboth':
                    all_object = User_Profile.objects.filter(is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman',
                                                        interested_in='editprofile_gender_checkboxwoman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman',
                                                        interested_in='editprofile_gender_checkboxman')

                elif interested_age and max_interested_age:
                    all_object = User_Profile.objects.filter(is_banned=False, age__range=(interested_age,
                                                                                                     max_interested_age))  # and like_and_dislike.objects.filter(user = request.user)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman')
                else:
                    all_object = User_Profile.objects.filter(city=city, is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman')
                profile = like_and_dislike.objects.filter(user=user_obj).values('user_profile_liked_or_dislike')
                all = all_object.exclude(user=self.request.user) and all_object.exclude(id__in=profile)
                all = all.exclude(appear_to_other=False)
                serializer = ProfilePostSerializer(all, many=True, context={"request": request})
                return Response({"All_Profiles": serializer.data}, status=status.HTTP_200_OK)
            else:
                if interested == 'editprofile_gender_checkboxboth' and interested_age and max_interested_age:
                    all_object = User_Profile.objects.filter(age__range=(interested_age, max_interested_age),
                                                             is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman',
                                                        interested_in='editprofile_gender_checkboxwoman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman',
                                                        interested_in='editprofile_gender_checkboxman')

                elif interested == 'editprofile_gender_checkboxboth':
                    all_object = User_Profile.objects.filter(is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman',
                                                        interested_in='editprofile_gender_checkboxwoman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman',
                                                        interested_in='editprofile_gender_checkboxman')

                elif interested_age and max_interested_age:
                    all_object = User_Profile.objects.filter(is_banned=False, age__range=(interested_age,
                                                                                    max_interested_age))  # and like_and_dislike.objects.filter(user = request.user)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman')
                else:
                    all_object = User_Profile.objects.filter(is_banned=False)
                    if user_obj.gender == 'editprofile_gender_checkboxman':
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxman')
                    else:
                        all_object = all_object.exclude(gender='editprofile_gender_checkboxwoman')
                profile = like_and_dislike.objects.filter(user=user_obj).values('user_profile_liked_or_dislike')
                all = all_object.exclude(id__in=profile)
                all = all.exclude(appear_to_other=False)
                all = all.exclude(id=user_obj.id)
                serializer = ProfilePostSerializer(all, many=True, context={"request": request})
                return Response({"All_Profiles": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Home Screen"}, status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def homescreen_filters(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user_obj != '':
            z = request.POST.get('distance')
            if z:
                # x, y = request.GET.get('latitude'), request.GET.get('longitude')
                z = int(z)
                user_coords = User_Profile.objects.filter(user=request.user).values('latitude', 'longitude')[0]
                all_user_coords = User_Profile.objects.all().values('latitude', 'longitude', 'user')
                x, y = user_coords.get('latitude'), user_coords.get('longitude')
                all_fillter_user_id = []
                for i in all_user_coords:
                    coords_2 = (i.get('latitude'), i.get('longitude'))
                    coords_1 = (x, y)
                    distance = geopy.distance.distance(coords_1, coords_2).km
                    if distance <= z:
                        fillter_user_id = i.get('user')
                        all_fillter_user_id.append(fillter_user_id)

                temp = request.POST.get('height')
                if temp:
                    temp = temp.split('.')
                    height = temp[0]
                    max_height = temp[1]
                else:
                    height = request.POST.get('height')
                    max_height = request.POST.get('max_height')

                # weight = request.GET.get('weight')
                education = request.POST.get('education')
                kids = request.POST.get('kids')
                drink = request.POST.get('drink')
                smoke = request.POST.get('smoke')
                city = request.POST.get('city')
                age = request.POST.get('age')
                interested_age = request.POST.get('interested_age')
                max_interested_age = request.POST.get('max_interested_age')
                exercise = request.POST.get('exercise')
                religion = request.POST.get('religion')

                list = {}
                set_if_not_none(list, 'user__in', all_fillter_user_id)
                set_if_not_none(list, 'height__gte', height)
                set_if_not_none(list, 'height__lte', max_height)
                set_if_not_none(list, 'education', education)
                set_if_not_none(list, 'kids', kids)
                set_if_not_none(list, 'drink', drink)
                set_if_not_none(list, 'smoke', smoke)
                set_if_not_none(list, 'city', city)
                set_if_not_none(list, 'age__gte', interested_age)
                set_if_not_none(list, 'age__lte', max_interested_age)
                set_if_not_none(list, 'exercise', exercise)
                set_if_not_none(list, 'religion', religion)
                # all_object = User_Profile.objects.filter(**list)
                if not education :
                    education = ""
                if not kids:
                    kids = ""
                if not drink:
                    drink = ""
                if not smoke:
                    smoke = ""
                if not city:
                    city = ""
                if not age:
                    age = 0
                if not interested_age:
                    interested_age = 0
                if not max_interested_age:
                    max_interested_age = 0
                if not exercise:
                    exercise = ""
                if not religion:
                    religion = ""
                history = FilterHistory(user_profile=user_obj,
                                        education=education,
                                        kids=kids,
                                        drink=drink,
                                        smoke=smoke,
                                        religion=religion,
                                        exercise=exercise,
                                        age=age,
                                        interested_age=interested_age,
                                        height =height,
                                        max_height=max_height,
                                        )
                history.save()     
                page = Pagination(request, 50)
                all_profile = page.advance_filter_pagination("User_Profile", list, user_obj)

                serializer = ProfilePostSerializer(all_profile, many=True, context={"request": request})
                return Response({"AllProfiles": serializer.data}, status=status.HTTP_200_OK)

            elif not z:

                temp = request.POST.get('height')
                if temp:
                    temp = temp.split('.')
                    height = temp[0]
                    max_height = temp[1]
                else:
                    height = request.POST.get('height')
                    max_height = request.POST.get('max_height')

                # weight = request.GET.get('weight')
                education = request.POST.get('education')
                kids = request.POST.get('kids')
                drink = request.POST.get('drink')
                smoke = request.POST.get('smoke')
                city = request.POST.get('city')
                age = request.POST.get('age')
                interested_age = request.POST.get('interested_age')
                max_interested_age = request.POST.get('max_interested_age')
                exercise = request.POST.get('exercise')
                religion = request.POST.get('religion')

                list = {}
                set_if_not_none(list, 'height__gte', height)
                set_if_not_none(list, 'height__lte', max_height)
                # set_if_not_none(list, 'weight__gte', weight)
                set_if_not_none(list, 'education', education)
                set_if_not_none(list, 'kids', kids)
                set_if_not_none(list, 'drink', drink)
                set_if_not_none(list, 'smoke', smoke)
                set_if_not_none(list, 'city', city)
                set_if_not_none(list, 'age__gte', interested_age)
                set_if_not_none(list, 'age__lte', max_interested_age)
                set_if_not_none(list, 'exercise', exercise)
                set_if_not_none(list, 'religion', religion)
                # all_object = User_Profile.objects.filter(**list)
                if not education :
                    education = ""
                if not kids:
                    kids = ""
                if not drink:
                    drink = ""
                if not smoke:
                    smoke = ""
                if not city:
                    city = ""
                if not age:
                    age = 0
                if not interested_age:
                    interested_age = 0
                if not max_interested_age:
                    max_interested_age = 0
                if not exercise:
                    exercise = ""
                if not religion:
                    religion = ""
                history = FilterHistory(user_profile=user_obj,
                                        education=education,
                                        kids=kids,
                                        drink=drink,
                                        smoke=smoke,
                                        religion=religion,
                                        exercise=exercise,
                                        age=age,
                                        interested_age=interested_age,
                                        height =height,
                                        max_height=max_height,
                                        )
                history.save()                              
                page = Pagination(request, 50)
                all_profile = page.advance_filter_pagination("User_Profile", list, user_obj)

                serializer = ProfilePostSerializer(all_profile, many=True, context={"request": request})
                return Response({"AllProfiles": serializer.data}, status=status.HTTP_200_OK)

            else:
                return Response({"Message": "Please Select Filter"}, status=status.HTTP_200_OK)


class like_and_dislikes(viewsets.ViewSet):  # like and dislike class

    def profiles_notification(self, **profile_data):
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
                "bodyText": "{}".format(profile_data['bodyText']),
                "organization": "You-Mee"
            }
        })
        headers = {
            'Authorization': 'key=AAAAxTKFuKU:APA91bEFiiTlF4IE5IC3VmLePPZUyVpMUnwXt8LwFYIXx777gSVyVnyypuy1PkbciYfeU-XS3KLJfXvf7BH_Fro-fOEWjDy6TUi7DJO6nOTDJTgWl9xsrdfVUxIbHp90drqWPyK6Fuqs',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

    @action(detail=False, methods=['post'])
    def like_dislike(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = qdict_to_dict(request.data)
        data['user'] = user_obj.id
        # objects = (like_and_dislike.objects.filter(user=user_obj, profile_status="Like")) and (
        #     like_and_dislike.objects.filter(user_profile_liked_or_dislike=user_obj, profile_status="Like",
        #                                     is_active='True')).values_list('user', flat=True).first()

        # Check if the other user has already liked the profile or not, if so created a chat room
        # and send match notification
        like_optimized = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike')
        objects = like_optimized.filter(user=data['user_profile_liked_or_dislike'], profile_status="Like",
                                        user_profile_liked_or_dislike=user_obj,
                                        is_active='True').values_list('user', flat=True).first()
        status_check = like_optimized.filter(user=user_obj, profile_status=data['profile_status'],
                                             user_profile_liked_or_dislike=data[
                                                 'user_profile_liked_or_dislike'])
        if objects and data['profile_status'] == "Like":
            chatroom_optimized = ChatRoom.objects.select_related('user1', 'user2', 'block_by')
            already_room = chatroom_optimized.filter(user1=user_obj.id, user2=objects) or ChatRoom.objects.filter(
                user1=objects, user2=user_obj)
            if already_room:
                return Response({'Message': 'Chat Room Already Exists'}, status=status.HTTP_200_OK)
            else:
                letters = string.ascii_lowercase
                name = ''.join(random.choice(letters)
                               for i in range(30))
                name = name
                like_serializer = LikeDislikeSerializer(data=data)
                serializer = ChatRoomSerializer(
                    data={"room_name": name, "user1": user_obj.id, "user2": objects, 'is_enabled': True})
                if serializer.is_valid() and like_serializer.is_valid():
                    like_serializer.save()
                    serializer.save()
                    login_user_fcm_token = user_obj.fcm_token
                    user_profiled_liked = User_Profile.objects.get(id=data['user_profile_liked_or_dislike'])
                    user_profiled_liked_token = user_profiled_liked.fcm_token
                    self.profiles_notification(tokens=user_profiled_liked_token, user_name='',
                                               title='Match Notification', bodyText='Match',
                                               msg="Vous avez un nouveau match! 🤎")
                    self.profiles_notification(tokens=login_user_fcm_token, user_name='',
                                               title='Match Notification', bodyText='Match',
                                               msg="Vous avez un nouveau match! 🤎")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        elif status_check:
            return Response({"Message": "Already Exists"}, status=status.HTTP_200_OK)
        else:
            serializer = LikeDislikeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if serializer.validated_data['profile_status'] == 'Like':
                    user_profiled_liked = User_Profile.objects.get(id=data['user_profile_liked_or_dislike'])
                    self.profiles_notification(tokens=user_profiled_liked.fcm_token,
                                               user_name=user_obj.your_name, title='Like Notification',
                                               bodyText='Like',
                                               msg=", vous plaisez à quelqu'un 😍 Ouvrez Youmee pour découvrir de qui il s'agit")
                return Response({'Message': 'Profile Updated'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def dislike_to_like(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        dic = request.data
        user_profile_liked_or_dislike_id = dic["user_profile_liked_or_dislike"]
        like = like_and_dislike.objects.filter(user=user_obj, profile_status="Dislike",
                                               user_profile_liked_or_dislike=user_profile_liked_or_dislike_id).update(
            profile_status="Like")
        if like == 1:
            sender = User_Profile.objects.get(id=user_profile_liked_or_dislike_id)
            sender_token = sender.fcm_token
            user_name = sender.your_name
            self.profiles_notification(tokens=sender_token, user_name=user_name, title='Like Notification',
                                       bodyText='Like',
                                       msg=", vous plaisez à quelqu'un 😍 Ouvrez Youmee pour découvrir de qui il s'agit")
            return Response({'Message': "Profile Status Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "Already Exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def like_to_dislike(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        dic = request.data
        user_profile_liked_or_dislike_id = dic["user_profile_liked_or_dislike"]
        dislike = like_and_dislike.objects.filter(user=user_obj, profile_status="Like",
                                                  user_profile_liked_or_dislike=user_profile_liked_or_dislike_id).update(
            profile_status="Dislike")
        if dislike == 1:
            if user_profile_liked_or_dislike_id in user_obj.cross_user_list:
                user_obj.cross_user_list.remove(user_profile_liked_or_dislike_id)
                user_obj.save()
            return Response({'Message': "Profile Status Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "Already Exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def who_like_you(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        # get all the user who liked this profile
        likes = like_and_dislike.objects.filter(user_profile_liked_or_dislike=user_obj,
                                                profile_status="Like").values_list('user', flat=True)
        ''' remove the users, who already had created matched with the profile. cross_user_list in user_profile model 
        stores the profiles with already matched created '''
        for x in likes:
            if str(x) in user_obj.cross_user_list:
                likes = likes.exclude(user=x)
        all_object = User_Profile.objects.filter(id__in=likes)
        serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
        return Response({"List_of_profiles_who_like_me": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def profile_i_dislike(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        dislikes = like_and_dislike.objects.filter(user=user_obj, profile_status="Dislike")
        dislikesa = like_and_dislike.objects.filter(user=user_obj, profile_status="Dislike").values(
            'user_profile_liked_or_dislike')

        all_object = User_Profile.objects.filter(id__in=dislikesa)
        serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
        return Response({"List_of_profiles_i_dislike": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def expaired_profiles(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        unactive_profiles = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
            .filter(user=user_obj, is_active=False)
        if unactive_profiles:
            expired = like_and_dislike.objects.filter(user=user_obj, is_active=False).values(
                "user_profile_liked_or_dislike")
            room_names = like_and_dislike.objects.filter(user__in=expired, is_active=False).values("user")
            all_object = User_Profile.objects.filter(id__in=expired)
            serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
            room_data = ChatRoom.objects.filter(user2__in=room_names) or ChatRoom.objects.filter(
                user1__in=room_names)
            room_data = ChatRoomSerializer(room_data, many=True)
            return Response({"List_of_profiles_expired": serializer.data, "Room": room_data.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"Message": "No Profiles"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def recover_profiles(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user_data = request.data.get('user_email')
        current_user = User_Profile.objects.filter(email=user_data).get().id
        recover_profile = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
            .filter(user=user_obj, is_active=False, counter=0, user_profile_liked_or_dislike=current_user)
        if recover_profile:
            new_status = True
            count = 1
            recover_profile.update(is_active=new_status, counter=1)
            like_and_dislike.objects.filter(user=user_obj, is_active=False).update(counter=count)
            return Response({"Message": "Profile Recovered", "Recovered": True}, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "Can Recover Profile After 24 Hours", "Recovered": False},
                            status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def cross_like(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        test = like_and_dislike.objects.filter(user=user_obj, profile_status="Like", is_active='True').values_list(
            'user_profile_liked_or_dislike__id', flat=True)
        test = list(test)
        objects = ((like_and_dislike.objects.filter(user=user_obj, user_profile_liked_or_dislike__in=test,
                                                    profile_status="Like", is_active='True')) and \
                   (like_and_dislike.objects.filter(user__in=test, user_profile_liked_or_dislike=user_obj,
                                                    profile_status="Like", is_active='True'))).exclude(
            user=user_obj).values_list("user", flat=True)
        all_object = User_Profile.objects.filter(id__in=objects)
        serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
        return Response({"List_of_cross_profiles": serializer.data}, status=status.HTTP_200_OK)


class PickForDating(viewsets.ModelViewSet):
    serializer_class = DatingSerializer
    http_method_names = ['get']

    def get_queryset(self):
        try:
            user_obj = User_Profile.objects.get(user=self.request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        # user who power liked me, would be pick for dating
        likesa = like_and_dislike.objects.filter(user_profile_liked_or_dislike=user_obj, profile_status="Super_like",
                                                 is_active=True).values('user')
        all_object = User_Profile.objects.filter(id__in=likesa)
        return all_object


class ProfileMatch(viewsets.ViewSet):  # New Profile Match class

    def get_queryset(self):
        try:
            user_obj = User_Profile.objects.get(user=self.request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        current_time = datetime.now()
        chat_room_details = ChatRoom.objects.filter(Q(user1=user_obj, is_enabled=True,
                                                      created_at__date=current_time.date()) |
                                                    Q(user2=user_obj, is_enabled=True,
                                                      created_at__date=current_time.date()))
        a = list()
        for x in chat_room_details:
            if x.user1 == user_obj:
                a.append(x.user2)
            else:
                a.append(x.user1)
        user_profiles_data = User_Profile.objects.filter(email__in=a)
        return user_profiles_data

    @action(detail=False, methods=['post'])
    def new_profile_match(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if user_obj.cross_user_list == []:
            test = like_and_dislike.objects.filter(user=user_obj, profile_status="Like", is_active='True',
                                                   match_seen=False) \
                .values_list('user_profile_liked_or_dislike__id', flat=True)
            test = list(test)
            objects_all = ((like_and_dislike.objects.filter(user=user_obj, user_profile_liked_or_dislike__in=test,
                                                            profile_status="Like", is_active='True',
                                                            match_seen=False))
                           and (like_and_dislike.objects.filter(user__in=test, user_profile_liked_or_dislike=user_obj,
                                                                profile_status="Like", is_active='True'))).exclude(
                user=user_obj).values_list("user", flat=True)
            # super_user = (like_and_dislike.objects.filter(user=user_obj, profile_status="Super_like",
            #                                               is_active='True', match_seen=False)).values_list(
            #     "user_profile_liked_or_dislike", flat=True)
            # objects_all = objects_all.union(super_user)
            if objects_all.exists():
                for event in objects_all:
                    if str(event) in user_obj.cross_user_list:
                        return Response({"Message": "You already match with this user previously"},
                                        status=status.HTTP_200_OK)
                    else:
                        matched_profile = User_Profile.objects.filter(id=event)
                        match_profiles = user_obj.cross_user_list
                        already_matched_profiles = User_Profile.objects.filter(id__in=match_profiles)
                        login_user = User_Profile.objects.filter(user=request.user)
                        serializer_user = ProfilePostSerializer(login_user, many=True, context={"request": request})
                        serializer = ProfilePostSerializer(matched_profile, many=True, context={"request": request})
                        already_matched_serializers = ProfilePostSerializer(already_matched_profiles, many=True,
                                                                            context={"request": request})
                        liked_profile = like_and_dislike.objects.filter(user=user_obj, profile_status="Like",
                                                                        match_seen=False,
                                                                        user_profile_liked_or_dislike=event)
                        if liked_profile:
                            liked_profile.update(match_seen=True)
                        user_obj.cross_user_list.append(event)
                        user_obj.save()
                        return Response({"like_user": serializer.data, "login_user": serializer_user.data,
                                         "all_like_user": already_matched_serializers.data},
                                        status=status.HTTP_200_OK)
            else:
                return Response({"Message": "There is no New Profile match"}, status=status.HTTP_200_OK)
        else:
            test = like_and_dislike.objects.filter(user=user_obj, profile_status="Like", is_active='True',
                                                   match_seen=False) \
                .values_list('user_profile_liked_or_dislike__id', flat=True)
            test = list(test)
            objects_all = ((like_and_dislike.objects.filter(user=user_obj, user_profile_liked_or_dislike__in=test,
                                                            profile_status="Like", is_active='True',
                                                            match_seen=False))
                           and (like_and_dislike.objects.filter(user__in=test,
                                                                user_profile_liked_or_dislike=user_obj,
                                                                profile_status="Like", is_active='True'))) \
                .exclude(user=user_obj).values_list("user", flat=True)
            # super_user = (like_and_dislike.objects.filter(user=user_obj, profile_status="Super_like",
            #                                               is_active='True', match_seen=False)).values_list(
            #     "user_profile_liked_or_dislike", flat=True)
            # objects_all = objects_all.union(super_user)
            if objects_all.exists():
                for event in objects_all:
                    if str(event) in user_obj.cross_user_list:
                        return Response({"Message": "You already match with this user previously"},
                                        status=status.HTTP_200_OK)
                    else:
                        matched_profile = User_Profile.objects.filter(id=event)
                        match_profiles = user_obj.cross_user_list
                        already_matched_profiles = User_Profile.objects.filter(id__in=match_profiles)
                        login_user = User_Profile.objects.filter(user=request.user)
                        serializer_user = ProfilePostSerializer(login_user, many=True, context={"request": request})
                        serializer = ProfilePostSerializer(matched_profile, many=True, context={"request": request})
                        already_matched_serializers = ProfilePostSerializer(already_matched_profiles, many=True,
                                                                            context={"request": request})
                        liked_profile = like_and_dislike.objects.filter(user=user_obj, profile_status="Like",
                                                                        match_seen=False,
                                                                        user_profile_liked_or_dislike=event)
                        if liked_profile:
                            liked_profile.update(match_seen=True)
                        user_obj.cross_user_list.append(event)
                        user_obj.save()
                        return Response({"like_user": serializer.data, "login_user": serializer_user.data,
                                         "all_like_user": already_matched_serializers.data},
                                        status=status.HTTP_200_OK)
            else:
                return Response({"Message": "There is no New Profile match"}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def recently_matched_profiles(self, request):
        recently_chat_profile = self.get_queryset()
        user_profile_serializer = ProfileScreenSerializer(recently_chat_profile, many=True,
                                                          context={'request': request})
        return Response({"user_profiles": user_profile_serializer.data}, status=status.HTTP_200_OK)


class Profile_Power_like(viewsets.ViewSet):  # Profile Power Like class
    @action(detail=False, methods=['post'])
    def Power_like(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user_obj.power_like_count == 1:
            user_data = request.data.get('user_email')
            current_user = User_Profile.objects.filter(email=user_data).get().id
            matched_profile = like_and_dislike.objects.select_related('user', 'user_profile_liked_or_dislike') \
                .filter(user=user_obj, user_profile_liked_or_dislike=current_user, profile_status='Super_like')
            if matched_profile:
                return Response({"Message": "Already Matched"}, status=status.HTTP_200_OK)
            else:
                new_data = request.data.copy()
                new_data['user'] = user_obj.id
                new_data['user_profile_liked_or_dislike'] = current_user
                new_data.update({'profile_status': 'Super_like'})
                serializer = LikeDislikeSerializer(data=new_data, context={"request": request})
                letters = string.ascii_lowercase
                name = ''.join(random.choice(letters)
                               for i in range(30))
                name = name
                chat_serializer = ChatRoomSerializer(
                    data={"room_name": name, "user1": user_obj.id, "user2": current_user, 'is_enabled': True})
                if serializer.is_valid() and chat_serializer.is_valid():
                    serializer.save()
                    chat_serializer.save()
                    User_Profile.objects.filter(user=request.user).update(power_like_count=0)
                    token = User_Profile.objects.filter(id=current_user).values_list('fcm_token',
                                                                                     flat=True).first()
                    url = "https://fcm.googleapis.com/fcm/send"

                    payload = json.dumps({
                        "to": token,
                        "notification": {
                            "body": "✨ Quelqu'un vous a envoyé un powerlike !",
                            "OrganizationId": "2",
                            "content_available": True,
                            "priority": "high",
                            "Title": "Power Like Notification"
                        },
                        "data": {
                            "priority": "high",
                            "sound": "app_sound.wav",
                            "content_available": True,
                            "bodyText": "New Power Like",
                            "organization": "You-Mee"
                        }
                    })
                    headers = {
                        'Authorization': 'key=AAAAxTKFuKU:APA91bEFiiTlF4IE5IC3VmLePPZUyVpMUnwXt8LwFYIXx777gSVyVnyypuy1PkbciYfeU-XS3KLJfXvf7BH_Fro-fOEWjDy6TUi7DJO6nOTDJTgWl9xsrdfVUxIbHp90drqWPyK6Fuqs',
                        'Content-Type': 'application/json'
                    }

                    response = requests.post(url, headers=headers, data=payload)
                    return Response({"Message": "Power like successful",
                                     "status": True, "data": serializer.data,
                                     "chat_data": chat_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": False, "error": serializer.errors,
                                     'chat_error': chat_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Message": "You have used your daily power like limit"}, status=status.HTTP_200_OK)


class user_block(viewsets.ViewSet):  # User Block class
    @action(detail=False, methods=['post'])
    def block(self, request):
        try:
            #       user_obj = User.objects.get(id=request.user.id)
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        data = qdict_to_dict(request.data)
        data['user'] = user_obj.id
        serializer = UserBlockSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'Message': 'This User is Successfully Block!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class country(viewsets.ViewSet):  # Countries
    @action(detail=False, methods=['post'])
    def add_country(self, request):
        try:
            country_exist = Countries.objects.filter(country_name=request.data['country_name'].capitalize()).values(
                'country_name')
            code_exist = Countries.objects.filter(code=request.data['code']).values(
                'code')
            if country_exist or code_exist:
                return Response({"Message": "Country or Code are Already exist"}, status=status.HTTP_404_NOT_FOUND)

            else:
                data = qdict_to_dict(request.data)
                serializer = CountrySerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'Message': 'New Country added!'}, status=status.HTTP_200_OK)
            return Response({"Message": "Please Enter Country Code Too..."}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({"Message": "Please Enter The Country Name and Code"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def show_cities(self, request):

        country_exist = Countries.objects.filter(country_name=request.data['country_name'].capitalize()).values(
            'country_name')
        user_city = City.objects.filter(all_country_name=request.data['country_name'].capitalize()).values('city_name')

        if country_exist:
            results = CitiesSerializer(user_city, many=True)

            return Response({"All_Cities": results.data})
        else:
            return Response({"Message": "Country Didn't Exist"})


class SocialLogin(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def login(self, request):
        # try:
        dic = request.data
        socialAuthToken = dic["accessToken"] or ""
        image = ''
        if "photoUrl" in dic:
            image = dic["photoUrl"]

        headers = {
            'Authorization': 'Bearer {0}'.format(socialAuthToken),
            "Content-Type": "application/json"}

        def Facebook():
            social_verification = requests.post("https://graph.facebook.com/v2.8/me", headers=headers)
            return social_verification.status_code == 200

        def Google(token):
            social_verification = requests.get(
                "https://www.googleapis.com/oauth2/v2/tokeninfo?access_token={0}".format(token))
            return social_verification.status_code == 200

        if (dic["provider"] == "FACEBOOK") or (dic["provider"] == "facebook"):
            is_valid = Facebook()
        elif (dic["provider"] == "google") or (dic["provider"] == "GOOGLE"):
            is_valid = Google(socialAuthToken)
        else:
            return Response({"msg": _("Provided information is not valid")}, status=status.HTTP_409_CONFLICT)

        profile = ''
        if is_valid:

            """if (email_verifying(request.data['email'])):
                    return generate_email_error()

                if (username_verifying(request.data['username'])):
                    return generate_username_error()
                """
            password = "{0}{1}{2}".format(dic["provider"], dic["id"], "youmee")

            if 'email' in dic and dic['email'] != None and dic['email'] != '':
                pass
            else:
                if "name" in dic and dic['name'] != "":
                    email_name = dic['name'].replace(' ', '-')
                    dic['email'] = email_name.lower() + dic['id'] + '@' + dic['provider'] + '.com'
                else:
                    dic['email'] = dic['provider'] + dic['id'] + '@' + dic['provider'] + '.com'
            if User.objects.filter(username=dic['email']).exists():
                object_user = User.objects.get(username=dic['email'])
                user = User_Profile.objects.filter(user=object_user).first()
                if user:
                    all_object = User_Profile.objects.filter(user=object_user.id)
                    serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})
                    if "name" in dic and dic['name'] != "":
                        name = dic['name']
                        name = name.split(' ')
                        object_user.first_name = name[0]
                        object_user.last_name = name[1]
                        object_user.save()
                    if image:
                        user.user_profile_image = image
                        user.save()
                else:
                    return Response({'Message': 'Something went Wrong!'}, status=status.HTTP_200_OK)

            else:
                object_user = User(username=dic['email'], email=dic['email'])
                if "name" in dic and dic['name'] != "":
                    name = dic['name']
                    name = name.split(' ')
                    object_user.first_name = name[0]
                    object_user.last_name = name[1]
                object_user.is_active = True
                object_user.set_password(raw_password=password)
                object_user.save()
                current_date = date.today().isoformat()
                expiry_date = (date.today() + timedelta(days=15)).isoformat()
                user_profile = User_Profile(user=object_user, email=object_user.email, package='VIP Plus',
                                            package_duration='15 Days Trial'
                                            , package_date_start=current_date,
                                            package_date_end=expiry_date)
                user_profile.save()
                user = User_Profile.objects.get(user=object_user)
                all_object = User_Profile.objects.filter(user=object_user.id)
                serializer = ProfilePostSerializer(all_object, many=True, context={"request": request})

            payload = jwt_payload_handler(object_user)
            token = jwt_encode_handler(payload)
            request.session["username"] = object_user.username
            return Response({"Token": token, "Role": user.role, "user_object": serializer.data, },
                            status=status.HTTP_200_OK)
        return Response({"msg": "Problem in Social Login!"},
                        status=status.HTTP_409_CONFLICT)


class Payment(viewsets.ViewSet):  # Payment class
    @action(detail=False, methods=['post'])
    def payment_check(self, request):
        try:
            user_obj = User_Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response({"Message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        temp = User_Profile.objects.filter(user=request.user).get().package_date_end.isoformat()
        current_date = date.today().isoformat()
        if current_date >= temp:
            User_Profile.objects.filter(user=request.user).update(package="null", package_duration="null",
                                                                  package_date_start=None, package_date_end=None)
        return Response({'Message': 'This User Profile is Successfully Update!'}, status=status.HTTP_200_OK)


class CitiesData(APIView):

    def post(self, request):
        x = self.request.data.get('country')
        payload = {"country": x}
        url = 'https://countriesnow.space/api/v0.1/countries/cities'
        response = requests.post(url, data=payload)
        json_data = json.loads(response.text)
        return Response(json_data['data'], status=status.HTTP_200_OK)


class PackageListViewSet(viewsets.ReadOnlyModelViewSet):
    from admin_panel.api.v1.serialziers import PackagesSerializer, Packages
    serializer_class = PackagesSerializer
    queryset = Packages.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.values('id', 'duration', 'price', 'name')
        classic_queryset = queryset.filter(name='Classic')
        classic_dict = dict()  # for storing classic values
        classic_vip_dict = dict()  # for storing classic plus values
        vip_dict = dict()  # for storing vip values
        vip_plus_dict = dict()  # for storing vip plus values
        for x in classic_queryset:
            if x['duration'] == '1 Month':
                classic_dict['month1'] = dict(x)
            elif x['duration'] == '3 Month':
                classic_dict['month3'] = dict(x)
            else:
                classic_dict['month6'] = dict(x)

        classic_vip_query = queryset.filter(name='Classic Plus')

        for y in classic_vip_query:
            if y['duration'] == '1 Month':
                classic_vip_dict['month1'] = dict(y)
            elif y['duration'] == '3 Month':
                classic_vip_dict['month3'] = dict(y)
            else:
                classic_vip_dict['month6'] = dict(y)

        vip_query = queryset.filter(name='VIP')
        for z in vip_query:
            if z['duration'] == '1 Month':
                vip_dict['month1'] = dict(z)
            elif z['duration'] == '3 Month':
                vip_dict['month3'] = dict(z)
            else:
                vip_dict['month6'] = dict(z)

        vip_plus_query = queryset.filter(name='VIP Plus')

        for k in vip_plus_query:
            if k['duration'] == '1 Month':
                vip_plus_dict['month1'] = dict(k)
            elif k['duration'] == '3 Month':
                vip_plus_dict['month3'] = dict(k)
            else:
                vip_plus_dict['month6'] = dict(k)

        context = {'Classic': classic_dict, 'Classic_Plus': classic_vip_dict,
                   'VIP': vip_dict, 'VIP_Plus': vip_plus_dict}

        return Response(context, status=status.HTTP_200_OK)


# class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = FilterHistorySerializer
#     queryset = FilterHistory.objects.all()
#     permission_classes = (IsAuthenticated,)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_history(request):
    try:
        user = User_Profile.objects.get(user=request.user)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},status=status.HTTP_404_NOT_FOUND)

    search_history=FilterHistory.objects.filter(user_profile=user)
    serializer = FilterHistorySerializer(search_history, many= True)
    return Response({'success': True, 'response': serializer.data},status=status.HTTP_200_OK)
