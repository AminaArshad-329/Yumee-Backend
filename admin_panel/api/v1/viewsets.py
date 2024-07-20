import json

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from admin_panel.models import ForgetPasswordTokens
from admin_panel.api.v1.serialziers import AdminUserSerializer, UserSerializer, BlockedUserSerializer
from core.models import User_Profile
from django.contrib.auth.models import User
import requests
from rest_framework.permissions import IsAdminUser, AllowAny


def email_sending(key, template, email, msg):
    from django.template.loader import get_template
    from django.core.mail import EmailMessage

    key = {'url': key}
    message = get_template(template).render(key)
    email = EmailMessage(msg, message, to=[email])
    email.content_subtype = 'html'
    email.send()


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000


class ForgetPassword(APIView):

    def post(self, request):
        email = request.data['email']
        if User.objects.filter(email=email, is_staff=True, is_active=True, is_superuser=True).exists():

            from string import ascii_lowercase
            from random import choice
            letters = ascii_lowercase
            new_token = ''.join(choice(letters) for i in range(11))
            ForgetPasswordTokens.objects.create(email=email, token=new_token)
            admin_user = User.objects.get(email=email)
            url = 'http://3.134.17.134/resetPassword/?id={0}&token={1}'.format(admin_user.id, new_token)
            email_sending(url, 'forget_password.html', email, 'Forget Password')
            return Response({"message": "Email has been sent"}, status=status.HTTP_200_OK)
        elif User_Profile.objects.filter(email=email).exists():
            return Response({"error": "Admin User Only"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Incorrect Email"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):

    def post(self, request):
        id = request.data['id']
        token = request.data['token']
        new_password = request.data['password']
        admin_user = ForgetPasswordTokens.objects.filter(token=token)
        if admin_user:
            from datetime import datetime, timedelta
            from pytz import utc
            current_time = datetime.now(utc).strftime("%m/%d/%Y, %H:%M:%S")
            admin_data = ForgetPasswordTokens.objects.get(token=token)
            token_expiry_time = (admin_data.created + timedelta(hours=1)).strftime("%m/%d/%Y, %H:%M:%S")
            # check the expiry of the token
            if current_time > token_expiry_time:
                return Response({'error': 'Link Expired, Try Again'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_obj = User.objects.get(email=admin_data.email)
                # check if the current and new password are same
                if user_obj.check_password(new_password):
                    return Response({'error': 'New and Current Password cannot be same.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_obj = User.objects.get(email=admin_data.email)
                    user_obj.set_password(new_password)
                    user_obj.save()
                    ForgetPasswordTokens.objects.get(token=token).delete()
                    return Response({'message': 'Password Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Link Expired, Try Again'}, status=status.HTTP_400_BAD_REQUEST)


class AdminLogin(viewsets.ViewSet):
    http_method_names = 'post'

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(email=email, is_active=True, is_staff=True, is_superuser=True).exists():
            admin_user = User.objects.get(email=email)
            url = 'http://18.221.70.79/core/login/'
            data1 = {"username": admin_user.username,
                     "password": password}
            user_data = User.objects.filter(email=email)
            serializer = AdminUserSerializer(user_data, many=True, context={"request": request})
            response = requests.post(url, data=data1).json()
            if 'token' in response:
                key = response['token']
                return Response({"Token": key, "admin_data": serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({"error": "Incorrect Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({"error": "Must be admin to login"}, status=status.HTTP_400_BAD_REQUEST)


class UserDataViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User_Profile.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['email', 'your_name']
    http_method_names = ['get', 'delete', 'patch']
    pagination_class = LargeResultsSetPagination

    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = User_Profile.objects.all()
        user_gender = self.request.query_params.get('gender')
        user_package = self.request.query_params.get('package')
        user_age = self.request.query_params.get('age')

        if user_age and user_gender and user_package is not None:
            if user_gender != 'gender':
                queryset = queryset.filter(gender=user_gender)
            if user_package != 'package':
                queryset = queryset.filter(package=user_package)
            if user_age != 'age':
                if user_age == "46":
                    queryset = queryset.filter(age__gte=46)
                else:
                    ages = str(user_age)
                    ages = ages.split("-")
                    queryset = queryset.filter(age__gte=ages[0], age__lte=ages[1])
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        from math import ceil
        page_count = queryset.count()
        if page_count <= 10:
            total_pages = 1
        else:
            total_pages = ceil(page_count / self.pagination_class.page_size)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            print(self.get_paginated_response(serializer.data))
            response = self.get_paginated_response(serializer.data)
            response.data['total_pages'] = total_pages
            return Response(data=response.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'total_pages': total_pages, 'result': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def admin_dashboard(self, request):
        query = User_Profile.objects.all()
        total_users = query.count()
        banned_users = query.filter(is_banned=True).count()
        active_user = query.filter(remaining_days_in_exp__gt=1).count()
        return Response({"total_users": total_users, "banned_users": banned_users, "active_users": active_user},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def temporary_delete_user(self, request, pk=None):
        try:
            user_id = self.get_object()
            if User_Profile.objects.filter(email=user_id).exists():
                user_banned_status = User_Profile.objects.get(email=user_id).is_banned
                if user_banned_status:
                    return Response({"error": 'User Already Temporarily Blocked'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    email = self.get_object()
                    url = 'contact@you-mee.com'
                    email_sending(url, 'ban_user.html', email, 'Bloquer le compte du client')
                    User_Profile.objects.filter(email=user_id).update(is_banned=True, is_restored=False)
                    return Response({"message": 'User Blocked Temporarily'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'No Such User'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def permanently_delete_user(self, request, pk=None):
        try:
            user_id = self.get_object()
            if User_Profile.objects.filter(email=user_id).exists():
                user_banned_status = User_Profile.objects.get(email=user_id).is_banned
                if not user_banned_status:
                    return Response({"error": 'You need to Temporary block this user first'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    User.objects.get(username=user_id).delete()
                    return Response({"message": 'User Deleted Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'No Such User'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=(AllowAny,))
    def restore_user(self, request, pk=None):
        try:
            user_id = self.get_object()
            if User_Profile.objects.filter(email=user_id).exists():
                user_banned_status = User_Profile.objects.get(email=user_id).is_banned
                if not user_banned_status:
                    return Response({"error": 'You need to Temporary block this user first'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    email = self.get_object()
                    url = 'contact@you-mee.com'
                    email_sending(url, 'restore_user.html', email, 'Récupération du compte')
                    User_Profile.objects.filter(email=user_id).update(is_banned=False, is_restored=True)
                    return Response({"message": 'User Restored Successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'No Such User'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_user(self, request, pk=None):
        user_id = self.get_object()
        User.objects.get(username=user_id).delete()
        return Response({"message": 'User Deleted Successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_selected_users(self, request):
        ids = request.data.get('selected_users')
        if ids is not None:
            for x in ids:
                user_data = User_Profile.objects.get(id=x)
                User.objects.filter(username=user_data.email).delete()
            if len(ids) == 1:
                return Response({'message': "User Deleted Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Users Deleted Successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "Selected Users Not Passed"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def export_user_csv(self, request):
        import csv
        from django.http import HttpResponse
        header = ['ID', 'Name', 'Email', 'DOB', 'Gender', 'Age', 'Interested In', 'City', 'Country',
                  'Do you have children', 'Education', 'Religion', 'Package', 'Package Duration',
                  'Package Start Date', 'Package End Date', 'Remaining Days In Expiry', 'Banned', 'Restored']

        def user_row(users):
            gender = ''
            interested_in = ''
            education = ''
            user_banned_status = ''
            user_restored_status = ''
            '''To convert gender into readable form'''
            if users.gender == 'editprofile_gender_checkboxwoman':
                gender = 'Female'
            if users.gender == 'editprofile_gender_checkboxman':
                gender = 'Male'

            '''To convert interested gender into readable form'''
            if users.interested_in == 'editprofile_gender_checkboxwoman':
                interested_in = 'Female'
            if users.interested_in == 'editprofile_gender_checkboxman':
                interested_in = 'Male'
            if users.interested_in == 'editprofile_gender_checkboxboth':
                interested_in = 'Both'

            '''To convert education into readable form'''
            if users.education == 'update_education_college_checkbox':
                education = 'College'
            if users.education == 'update_education_highschool_checkbox':
                education = 'High School'
            if users.education == 'update_education_BAC_checkbox':
                education = 'BAC Level'
            if users.education == 'update_university_checkbox':
                education = 'University Diploma'

            '''Convert banned and restored status boolean values to yes or no'''
            if users.is_banned is True:
                user_banned_status = 'Yes'
            if users.is_banned is False:
                user_banned_status = 'No'

            if users.is_restored is True:
                user_restored_status = 'Yes'
            if users.is_restored is False:
                user_restored_status = 'No'

            if users.package == '':
                package = "Not Subscribed"
            else:
                package = users.package

            if users.package_duration == '':
                package_duration = "Not Subscribed"
            else:
                package_duration = users.package_duration

            if users.kids == 'partener_kids_yes':
                kids = 'Yes'
            elif users.kids == 'partener_kids_no':
                kids = 'No'
            else:
                kids = 'Not Mentioned'

            row = [users.id, users.your_name, users.email, users.date_of_birth, gender, users.age,
                   interested_in, users.city, users.country, kids, education, users.religion, package,
                   package_duration, users.package_date_start, users.package_date_end,
                   users.remaining_days_in_exp, user_banned_status, user_restored_status]
            return row

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.writer(response)
        writer.writerow(header)
        for users in self.queryset:
            writer.writerow(user_row(users))
        return response


class BlockerUserViewSet(viewsets.ModelViewSet):
    from chat.models import ChatRoom
    serializer_class = BlockedUserSerializer
    queryset = ChatRoom.objects.filter(is_enabled=False)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ['block_user__email', 'block_user__your_name']
    pagination_class = LargeResultsSetPagination

    # permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        from math import ceil
        page_count = queryset.count()
        if page_count <= 10:
            total_pages = 1
        else:
            total_pages = ceil(page_count / self.pagination_class.page_size)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_pages'] = total_pages
            return Response(data=response.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'total_pages': total_pages, 'result': serializer.data}, status=status.HTTP_200_OK)


class PackagesViewSet(viewsets.ModelViewSet):
    from admin_panel.api.v1.serialziers import PackagesSerializer, Packages
    serializer_class = PackagesSerializer
    queryset = Packages.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = (IsAdminUser,)

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

    def create(self, request, *args, **kwargs):
        # this method is used for the package price update.
        package_data = request.data
        try:
            queryset = self.queryset.filter(name=package_data['name'],
                                            duration=package_data['duration'], price=package_data['price'])
            if queryset:
                return Response({'error': 'Same Price Exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if request.data['price'] == 0 or request.data['price'] < 0:
                    return Response({'error': "Value must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    queryset = self.queryset.filter(name=package_data['name'], duration=package_data['duration']). \
                        update(price=package_data['price'])
                    return Response({'message': 'Price Updated Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            if e.args[0] == "integer out of range\n":
                return Response({'error': 'Price figure should be less than 9 values'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Package {} not defined'.format(e.args[0])},
                                status=status.HTTP_400_BAD_REQUEST)
