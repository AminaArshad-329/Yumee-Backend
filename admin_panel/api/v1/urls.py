from django.urls import path, include
from admin_panel.api.v1.viewsets import UserDataViewSet, AdminLogin, ForgetPassword, ResetPassword,\
        BlockerUserViewSet, PackagesViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('user_data', UserDataViewSet, basename='user_data')
router.register('blocked_user_list', BlockerUserViewSet, basename='blocked_users')
router.register('packages_list', PackagesViewSet, basename='packages_list')

urlpatterns = [
        path('', include(router.urls)),
        path('admin_login/', AdminLogin.as_view({'post': 'post'}), name='admin_login'),
        path('forget_password/', ForgetPassword.as_view(), name='forget_password'),
        path('rest_password/', ResetPassword.as_view(), name='rest_password')
]