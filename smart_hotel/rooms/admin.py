from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path

from .models import User, RoomType, Room, Booking, BookingDetail, Service, BookingService, Payment, Review


# 1. Cấu hình hiển thị cho User
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    readonly_fields = ['image_view']

    # Thêm các trường custom vào màn hình chỉnh sửa chi tiết
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone_number', 'role', 'avatar', 'image_view')}),
    )

    def image_view(self, user):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" width="200" style="border-radius: 8px;"/>')
        return None


# 2. Cấu hình hiển thị cho RoomType (giữ nguyên logic của bạn, thêm list_display)
class MyRoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'capacity', 'active')
    search_fields = ('name',)
    list_filter = ('active',)
    readonly_fields = ['image_view']

    def image_view(self, room_type):
        if room_type.image:
            return mark_safe(f'<img src="{room_type.image.url}" width="200" style="border-radius: 8px;"/>')
        return None


# 3. Cấu hình hiển thị cho Room (giữ nguyên logic của bạn, thêm list_display)
class MyRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'status', 'active')
    list_filter = ('status', 'room_type', 'active')
    search_fields = ('room_number',)
    readonly_fields = ['image_view']

    def image_view(self, room):
        if room.image:
            return mark_safe(f'<img src="{room.image.url}" width="200" style="border-radius: 8px;"/>')
        return None


# 4. Cấu hình hiển thị cho Service (Dịch vụ) - Áp dụng image_view
class MyServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active')
    search_fields = ('name',)
    readonly_fields = ['image_view']

    def image_view(self, service):
        if service.image:
            return mark_safe(f'<img src="{service.image.url}" width="200" style="border-radius: 8px;"/>')
        return None

# 5. Cấu hình hiển thị cho Booking (Đặt phòng)
class MyBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'check_in_date', 'check_out_date', 'status', 'total_amount')
    list_filter = ('status', 'check_in_date')
    search_fields = ('customer__username', 'customer__email')


# 6. Cấu hình hiển thị cho Payment (Thanh toán)
class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_method', 'payment_status', 'created_date')
    list_filter = ('payment_status', 'payment_method')


# Cấu hình Custom Admin Site
class MyAdminSite(admin.AdminSite):
    site_header = "Smart Hotel Admin"
    site_title = "Smart Hotel Portal"
    index_title = "Quản trị hệ thống khách sạn"

    def get_urls(self):
        return [
            path('room-stats/', self.room_stats),
        ] + super().get_urls()

    def room_stats(self, request):
        stats = RoomType.objects.annotate(count=Count('room')).values('id', 'name', 'count')
        return TemplateResponse(request, "admin/stats.html", {"stats": stats})

# Khởi tạo
admin_site = MyAdminSite()

admin_site.register(User, MyUserAdmin)
admin_site.register(RoomType, MyRoomTypeAdmin)
admin_site.register(Room, MyRoomAdmin)
admin_site.register(Service, MyServiceAdmin)
admin_site.register(Booking, MyBookingAdmin)
admin_site.register(Payment, MyPaymentAdmin)

# Các bảng chi tiết không cần custom giao diện nhiều có thể đăng ký trực tiếp
admin_site.register(BookingDetail)
admin_site.register(BookingService)
admin_site.register(Review)