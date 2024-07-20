from django.urls import path, include

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token
from .views import *

router = routers.DefaultRouter()
router.register(r'user_profile', User_Profiles, basename='User')  # get auth user infoSSS
router.register(r'password', password, basename='Password')  # get auth user infoSSS
router.register(r'homescreen', homescreen, basename='Homescreen')
router.register(r'like_and_dislikes', like_and_dislikes, basename='like_and_dislikes')
router.register(r'profile_match', ProfileMatch, basename='profile_match')
router.register(r'Profile_Power_like', Profile_Power_like, basename='Profile_Power_like')
router.register(r'user_block', user_block, basename='user_block')
router.register(r'country', country, basename='country')
router.register(r'social_login', SocialLogin, basename='sociallogin')
router.register(r'payment', Payment, basename='payment')
router.register(r'pick_for_dating', PickForDating, basename='pick_for_dating')
router.register(r'package_list', PackageListViewSet, basename='package_list')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_jwt_token),  # login
    path('cities_data/', CitiesData.as_view(), name='cities_data'),
    path('searchhistory/',search_history)
    
]
