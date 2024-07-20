# notification/urls.py
from django.urls import path

from . import views
from .views import  SendNotification, NotificationList, SingleNotification, UpdateDeleteNotification, NotificationRoomInfo

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:user_id>/', views.room, name='room'),
    # path('api/', NotificationList.as_view(), name="allnotification"),
    path('api/notification_room_info/', NotificationRoomInfo.as_view(), name="notification_room_info"),
    path('api/list/', NotificationList.as_view(), name="allnotification"),
    path('api/singlenotification/<str:pk>/', SingleNotification.as_view(), name="notification"),
    path('api/create', SendNotification.as_view(), name="create"),
    # path('api/update/<str:pk>/', UpdateDeleteNotification.as_view(), name="update"),
    path('api/update/<int:pk>/', UpdateDeleteNotification.as_view(), name="update"),
    # path('api/delete/<str:pk>/', views.notificationDelete, name="delete"),
    # path("api/",views.ListTodoAPIView.as_view(),name="todo_list"),
    # path("api/create/", views.CreateTodoAPIView.as_view(),name="todo_create"),
    # path("api/update/<int:pk>/",views.UpdateTodoAPIView.as_view(),name="update_todo"),
    # path("api/delete/<int:pk>/",notification_delete.as_view(),name="delete"),
    # path("sociallogin/", SocialLogin.as_view()),
]