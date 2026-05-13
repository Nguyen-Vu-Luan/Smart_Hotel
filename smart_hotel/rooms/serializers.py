from rest_framework import serializers
from rooms.models import Room, RoomType, User

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'status', 'image', 'room_type']


    #  ghi đè không ảnh hưởng tới Deserializer
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data['image'] = instance.image.url
        return data