from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path

from .models import RoomType, Room


class MyRoomTypeAdmin(admin.ModelAdmin):
    readonly_fields = ['image_view']

    def image_view(self, room_type):
        if room_type.image:
            return mark_safe(f'<img src="{room_type.image.url}" width="200"/>')
        return None

class MyRoomAdmin(admin.ModelAdmin):
    readonly_fields = ['image_view']
    def image_view(self, room):
        if room.image:
            return mark_safe(f'<img src="{room.image.url}" width="200"/>')
        return None



# class RoomTypeAdmin(admin.ModelAdmin):


class MyAdminSite(admin.AdminSite):
    site_header = "Smart Hotel Admin"

    def get_urls(self):
        return [
            path('room-stats/', self.room_stats),
        ] + super().get_urls()

    def room_stats(self, request):
        stats = RoomType.objects.annotate(count=Count('room')).values('id', 'name', 'count')
        return TemplateResponse(request, "admin/stats.html", {"stats": stats})

admin_site = MyAdminSite()
admin_site.register(RoomType, MyRoomTypeAdmin)
admin_site.register(Room, MyRoomAdmin)