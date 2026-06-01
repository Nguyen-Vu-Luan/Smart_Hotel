from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rooms import views
from .admin import admin_site

r = DefaultRouter()
r.register('roomtypes', views.RoomTypeViewSet, 'roomtype')
r.register('rooms', views.RoomViewSet, 'room')
r.register('users', views.UserViewSet, 'user')
r.register('services', views.ServiceViewSet, basename='service')
r.register('bookings', views.BookingViewSet, basename='booking')
r.register('booking-services', views.BookingServiceViewSet, basename='booking-service')
r.register('payments', views.PaymentViewSet, basename='payment')
r.register('reviews', views.ReviewViewSet, basename='review')


urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include(r.urls)),
]