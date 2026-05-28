from rest_framework import serializers
from rooms.models import Room, RoomType, Service, BookingDetail, BookingService, Payment, Booking, Review
from django.contrib.auth import get_user_model
from django.db import transaction

# API của User
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
        return user


#API của RoomType
class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

    # Xử lý URL ảnh cho Loại phòng
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
        return data


# API của Room
class RoomSerializer(serializers.ModelSerializer):
    # Nhúng thêm chi tiết Loại phòng (chỉ đọc) để Frontend tiện hiển thị giá, tên loại
    room_type_info = RoomTypeSerializer(source='room_type', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'status', 'image', 'room_type', 'room_type_info', 'active']

    #  ghi đè không ảnh hưởng tới Deserializer
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data['image'] = instance.image.url
        return data


# API của Service
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'image', 'active']

    # Xử lý URL ảnh Cloudinary tương tự RoomType
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
        return data


# API của BookingService
class BookingServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingService
        fields = ['id', 'booking', 'service', 'quantity', 'total_price']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        # Tự động tính tổng tiền = số lượng * đơn giá của service
        service = validated_data['service']
        validated_data['total_price'] = service.price * validated_data['quantity']
        return super().create(validated_data)


#  API của Payment
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'payment_status', 'created_date']
        read_only_fields = ['payment_status'] # Chỉ Admin/Hệ thống mới được đổi trạng thái thành SUCCESS


# API của Review
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment', 'created_date']

class PublicReviewSerializer(serializers.ModelSerializer):
    # Lấy thông tin khách hàng từ Booking -> Customer
    customer_name = serializers.CharField(source='booking.customer.full_name', read_only=True)
    customer_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        # Chỉ trả về các trường cần thiết cho cộng đồng xem, ẩn ID của booking đi
        fields = ['id', 'rating', 'comment', 'created_date', 'customer_name', 'customer_avatar']

    # Xử lý URL ảnh Avatar qua Cloudinary
    def get_customer_avatar(self, obj):
        if obj.booking.customer.avatar:
            return obj.booking.customer.avatar.url
        return None

# API của BookingDetail
class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = ['id', 'room', 'price_at_booking']
        read_only_fields = ['price_at_booking']

# API của Booking
class BookingSerializer(serializers.ModelSerializer):
    details = BookingDetailSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'check_in_date', 'check_out_date', 'status', 'special_requests', 'total_amount',
                  'details', 'created_date']
        # Chỉ đọc: customer (lấy từ token), status (mặc định PENDING), total_amount (Backend tự tính)
        read_only_fields = ['customer', 'status', 'total_amount']

    @transaction.atomic  # Đảm bảo rollback nếu có lỗi xảy ra giữa chừng
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        # Gán customer từ context của request
        validated_data['customer'] = self.context['request'].user

    # @transaction.atomic
    # def create(self, validated_data):
    #     details_data = validated_data.pop('details')
    #
    #     # 🚀 LẤY USER TỪ REQUEST
    #     user = self.context['request'].user
    #
    #     # Mẹo: Nếu Front-end chưa đăng nhập (user là AnonymousUser), tự bốc đại User đầu tiên trong DB để test luồng
    #     if user.is_anonymous:
    #         user = User.objects.first()
    #         if not user:
    #             raise serializers.ValidationError({
    #                                                   "error": "Database chưa có User nào để gán đơn hàng test. Hãy tạo 1 user trong Django Admin trước!"})
    #
    #     validated_data['customer'] = user

        # 1. Tạo Booking
        booking = Booking.objects.create(**validated_data)

        total_room_price = 0
        # 2. Tạo các BookingDetail
        for detail_data in details_data:
            room = detail_data['room']
            # Lấy giá của loại phòng tại thời điểm đặt (để điền vào price_at_booking)
            price = room.room_type.base_price
            BookingDetail.objects.create(booking=booking, room=room, price_at_booking=price)
            total_room_price += price

        # 3. Cập nhật tổng tiền (Tạm tính đơn giản: Giá phòng * Số đêm. Ở đây minh họa bằng giá phòng)
        booking.total_amount = total_room_price
        booking.save()

        return booking