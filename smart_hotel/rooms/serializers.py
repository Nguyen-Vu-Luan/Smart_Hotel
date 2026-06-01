from rest_framework import serializers
from rooms.models import Room, RoomType, Service, BookingDetail, BookingService, Payment, Booking, Review, User
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleUserSerializer.Meta.model
        fields = SimpleUserSerializer.Meta.fields + ['username', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
        return data


class RoomSerializer(serializers.ModelSerializer):
    room_type_info = RoomTypeSerializer(source='room_type', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'status', 'image', 'room_type', 'room_type_info', 'active']


    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data['image'] = instance.image.url
        return data



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'image', 'active']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
        return data



class BookingServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingService
        fields = ['id', 'booking', 'service', 'quantity', 'total_price']
        read_only_fields = ['total_price']

    def create(self, validated_data):

        service = validated_data['service']
        validated_data['total_price'] = service.price * validated_data['quantity']
        return super().create(validated_data)



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'payment_status', 'created_date']
        read_only_fields = ['payment_status']



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment', 'created_date']

class PublicReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='booking.customer.full_name', read_only=True)
    customer_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_date', 'customer_name', 'customer_avatar']

    def get_customer_avatar(self, obj):
        if obj.booking.customer.avatar:
            return obj.booking.customer.avatar.url
        return None


class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = ['id', 'room', 'price_at_booking']
        read_only_fields = ['price_at_booking']


class BookingSerializer(serializers.ModelSerializer):
    details = BookingDetailSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'check_in_date', 'check_out_date', 'status', 'special_requests', 'total_amount',
                  'details', 'created_date']
        read_only_fields = ['customer', 'status', 'total_amount']

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        validated_data['customer'] = self.context['request'].user


        booking = Booking.objects.create(**validated_data)

        total_room_price = 0

        for detail_data in details_data:
            room = detail_data['room']
            price = room.room_type.base_price
            BookingDetail.objects.create(booking=booking, room=room, price_at_booking=price)
            total_room_price += price


        booking.total_amount = total_room_price
        booking.save()

        return booking