from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rooms import views

r = DefaultRouter()
r.register('roomtypes', views.RoomTypeViewSet, 'roomtype')
r.register('rooms', views.RoomTypeViewSet, 'room')
r.register('users', views.UserViewSet, 'user')
r.register('services', views.ServiceViewSet, basename='service')
r.register('bookings', views.BookingViewSet, basename='booking')
r.register('booking-services', views.BookingServiceViewSet, basename='booking-service')
r.register('payments', views.PaymentViewSet, basename='payment')
r.register('reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(r.urls)),
]