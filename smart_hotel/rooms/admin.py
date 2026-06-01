from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path

from .models import User, RoomType, Room, Booking, BookingDetail, Service, BookingService, Payment, Review
from .utils import get_stats_data

class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    readonly_fields = ['image_view']


    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone_number', 'role', 'avatar', 'image_view')}),
    )

    def image_view(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" width="200" style="border-radius: 8px;"/>')
        return None



class MyRoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'capacity', 'active')
    search_fields = ('name',)
    list_filter = ('active',)
    readonly_fields = ['image_view']

    def image_view(self, room_type):
        if room_type.image:
            return mark_safe(f'<img src="{room_type.image.url}" width="200" style="border-radius: 8px;"/>')
        return None



class MyRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'status', 'active')
    list_filter = ('status', 'room_type', 'active')
    search_fields = ('room_number',)
    readonly_fields = ['image_view']

    def image_view(self, room):
        if room.image:
            return mark_safe(f'<img src="{room.image.url}" width="200" style="border-radius: 8px;"/>')
        return None


class MyServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active')
    search_fields = ('name',)
    readonly_fields = ['image_view']

    def image_view(self, service):
        if service.image:
            return mark_safe(f'<img src="{service.image.url}" width="200" style="border-radius: 8px;"/>')
        return None

class MyBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'check_in_date', 'check_out_date', 'status', 'total_amount')
    list_filter = ('status', 'check_in_date')
    search_fields = ('customer__username', 'customer__email')



class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_method', 'payment_status', 'created_date')
    list_filter = ('payment_status', 'payment_method')



class MyAdminSite(admin.AdminSite):
    site_header = "Smart Hotel Admin"
    site_title = "Smart Hotel Portal"
    index_title = "Quản trị hệ thống khách sạn"

    def get_urls(self):
        return [
            path('stats/', self.stats_view, name='stats_view')
        ] + super().get_urls()


    def stats_view(self, request):
        year = int(request.GET.get('year', 2026))
        period = request.GET.get('period', 'month')
        data = get_stats_data(period, year)
        return TemplateResponse(request, 'admin/stats.html', {
            'data': data, 'year': year, 'period': period
        })



admin_site = MyAdminSite()

admin_site.register(User, MyUserAdmin)
admin_site.register(RoomType, MyRoomTypeAdmin)
admin_site.register(Room, MyRoomAdmin)
admin_site.register(Service, MyServiceAdmin)
admin_site.register(Booking, MyBookingAdmin)
admin_site.register(Payment, MyPaymentAdmin)

admin_site.register(BookingDetail)
admin_site.register(BookingService)
admin_site.register(Review)
