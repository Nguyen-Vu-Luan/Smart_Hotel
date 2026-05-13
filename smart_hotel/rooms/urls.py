from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rooms import views

r = DefaultRouter()
r.register('roomtypes', views.RoomTypeViewSet, 'roomtype')
r.register('rooms', views.RoomTypeViewSet, 'room')

urlpatterns = [
    path('', include(r.urls)),
]