from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

# 1. Bảng User (Người dùng)
class User(AbstractUser):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Khách hàng'),
        ('RECEPTIONIST', 'Lễ tân'),
        ('HOUSEKEEPING', 'Dọn phòng'),
        ('ACCOUNTANT', 'Kế toán'),
        ('MANAGER', 'Quản lý'),
    ]
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    avatar = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.username

# Base dùng cho các thuộc tính chung
class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 2. Bảng RoomType (Loại phòng)
class RoomType(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    image = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.name

# 3. Bảng Room (Phòng)
class Room(BaseModel):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Trống'),
        ('OCCUPIED', 'Đang có khách'),
        ('CLEANING', 'Đang dọn dẹp'),
        ('MAINTENANCE', 'Bảo trì'),
    ]

    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.room_number

# 4. Bảng Booking (Đặt phòng)
class Booking(BaseModel):
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('CHECKED_IN', 'Đang ở'),
        ('CHECKED_OUT', 'Đã trả phòng'),
        ('CANCELLED', 'Đã hủy'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    special_requests = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Booking #{self.id} - {self.customer.username}"

# 5. Bảng BookingDetail (Chi tiết đặt phòng)
class BookingDetail(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='details')
    # Sử dụng PROTECT để không cho phép xóa phòng nếu đã có người đặt
    room = models.ForeignKey('Room', on_delete=models.PROTECT, related_name='booking_details')
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detail #{self.id} for Booking #{self.booking.id}"

# 6. Bảng Service (Dịch vụ đi kèm)
class Service(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.name

# 7. Bảng BookingService (Dịch vụ khách đã đặt)
class BookingService(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='services')
    # Sử dụng PROTECT để lịch sử hóa đơn không bị lỗi nếu lỡ xóa Service
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.service.name} (Booking #{self.booking.id})"

# 8. Bảng Payment (Thanh toán)
class Payment(BaseModel):
    METHOD_CHOICES = [
        ('CARD', 'Thẻ ngân hàng'),
        ('E_WALLET', 'Ví điện tử'),
        ('CASH', 'Trực tiếp tại quầy'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Chờ thanh toán'),
        ('SUCCESS', 'Thành công'),
        ('FAILED', 'Thất bại'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Payment #{self.id} - {self.payment_status}"

# 9. Bảng Review (Đánh giá)
class Review(BaseModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Review for Booking #{self.booking.id}"