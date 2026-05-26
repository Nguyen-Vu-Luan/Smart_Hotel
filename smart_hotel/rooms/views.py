from rest_framework import viewsets, generics, filters, status, parsers, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import RoomType, Room, User, Service, Booking, BookingService, Payment, Review
from rooms import serializers, paginators
from rest_framework.decorators import action
from rest_framework.response import Response
from rooms.vnpay_helpers import VNPayHelper
from .utils import send_invoice_email
from .perms import IsReviewOwner



# Viewset của User
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False, permission_classes = [permissions.IsAuthenticated])
    def current_user(self, request):
        u = request.user
        if request.method.__eq__('PATCH'):
            s = serializers.SimpleUserSerializer(u, data=request.data)
            s.is_valid(raise_exception=True)
            u = s.save()

        return Response(serializers.UserSerializer(u).data, status=status.HTTP_200_OK)


# Viewset của Roomtype
class RoomTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    # Chỉ lấy các loại phòng đang hoạt động
    queryset = RoomType.objects.filter(active=True)
    serializer_class = serializers.RoomTypeSerializer

    @action(methods=['get'], detail=True, url_path='reviews', permission_classes=[permissions.AllowAny])
    def get_reviews(self, request, pk=None):
        # 1. Lấy loại phòng hiện tại dựa trên ID (pk) truyền vào URL
        room_type = self.get_object()

        # 2. Truy vấn chéo (JOIN): Tìm các Review thuộc về Booking có chứa Room thuộc RoomType này
        # Logic: Review -> Booking -> BookingDetail -> Room -> RoomType
        reviews = Review.objects.filter(
            booking__details__room__room_type=room_type
        ).distinct()  # distinct() để tránh trùng lặp dữ liệu nếu 1 booking đặt 2 phòng cùng loại

        # 3. Serialize dữ liệu và trả về
        serializer = serializers.PublicReviewSerializer(reviews, many=True)
        return Response(serializer.data)

# Viewset của Room
class RoomViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Room.objects.filter(active=True)
    serializer_class = serializers.RoomSerializer
    pagination_class = paginators.ItemPaginator

    # Cách 1 để lọc bằng get_queryset

    # Cách 1 để lọc
    # Tìm liếm theo q và roomtpye_id
    # def get_queryset(self):
    #     query = self.request
    #
    #     q = self.request.query_params.get('q')
    #     if q:
    #         query = query.filter(subject__icontains=q)
    #
    #     roomtype_id = self.request.query_params.get('room_type_id')
    #     if roomtype_id:
    #         query = query.filter(roomtype_id=roomtype_id)
    #     return query

    # Cách 2 để lọc dùng BUILD-IN FILTERS
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    # Lọc chính xác (Exact match)
    filterset_fields = ['room_type', 'status']
    # tìm kiếm theo từ khóa (?search=...)
    search_fields = ['room_number']
    # Sắp xếp (?ordering=...)
    ordering_fields = ['room_type_id']

    @action(methods=['post'], detail=True, url_path='finish-cleaning')
    def finish_cleaning(self, request, pk=None):
        if request.user.role not in ['HOUSEKEEPING', 'MANAGER']:
            return Response({"error": "Bạn không thuộc bộ phận dọn phòng để thực hiện thao tác này!"},
                            status=status.HTTP_403_FORBIDDEN)

        room = self.get_object()

        if room.status != 'CLEANING':
            return Response({"error": "Phòng này hiện tại không ở trạng thái cần dọn dẹp!"},
                            status=status.HTTP_400_BAD_REQUEST)

        room.status = 'AVAILABLE'
        room.save()

        return Response({"message": f"Phòng {room.room_number} đã được dọn sạch sẽ và sẵn sàng đón khách!"},
                        status=status.HTTP_200_OK)



# Viewset của Service
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(active=True)
    serializer_class = serializers.ServiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# Viewset của Service (Yêu cầu đăng nhập)
class BookingServiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookingServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ xem các dịch vụ thuộc các booking của user này
        return BookingService.objects.filter(booking__customer=self.request.user)


# Viewset của Payment (Yêu cầu đăng nhập)
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(booking__customer=self.request.user)

    @action(methods=['post'], detail=False, url_path='create-vnpay')
    def create_vnpay_payment(self, request):
        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Đơn đặt phòng không tồn tại hoặc không thuộc quyền sở hữu của bạn!"},
                            status=status.HTTP_404_NOT_FOUND)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'payment_method': 'E_WALLET',
                'payment_status': 'PENDING'
            }
        )

        payment_url = VNPayHelper.get_payment_url(
            booking_id=booking.id,
            amount=booking.total_amount,
            order_desc=f"Thanh toan hoa don dat phong #{booking.id} tai Smart Hotel",
            ip_address=ip_address
        )

        return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='vnpay-callback', permission_classes=[permissions.AllowAny])
    def vnpay_callback(self, request):
        query_params = request.GET.dict()

        if VNPayHelper.validate_response(query_params):
            booking_id = query_params.get('vnp_TxnRef')
            response_code = query_params.get('vnp_ResponseCode')

            try:
                booking = Booking.objects.get(id=booking_id)
                payment = Payment.objects.get(booking=booking)

                if response_code == '00':
                    payment.payment_status = 'SUCCESS'
                    booking.status = 'CONFIRMED'
                    payment.save()
                    booking.save()
                    send_invoice_email(booking)
                    return Response({"message": "Thanh toán qua cổng VNPay thành công!"}, status=status.HTTP_200_OK)
                else:
                    payment.payment_status = 'FAILED'
                    payment.save()
                    return Response({"error": f"Thanh toán thất bại hoặc đã bị hủy. Mã lỗi: {response_code}"},
                                    status=status.HTTP_400_BAD_REQUEST)

            except (Booking.DoesNotExist, Payment.DoesNotExist):
                return Response({"error": "Không tìm thấy dữ liệu hóa đơn trùng khớp với mã phản hồi"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Chữ ký bảo mật không khớp (Checksum failed)!"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='pay-at-counter')
    def pay_at_counter(self, request):
        if request.user.role not in ['RECEPTIONIST', 'MANAGER']:
            return Response({"error": "Bạn không có quyền thực hiện chức năng này!"},
                            status=status.HTTP_403_FORBIDDEN)

        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn đặt phòng"}, status=status.HTTP_404_NOT_FOUND)

        payment, created = Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'payment_method': 'CASH',  # Trực tiếp tại quầy
                'payment_status': 'SUCCESS'
            }
        )

        booking.status = 'CONFIRMED'
        booking.save()

        send_invoice_email(booking)

        return Response({"message": "Nhân viên đã xác nhận thanh toán tiền mặt thành công!"},
                        status=status.HTTP_200_OK)


# Viewset của Review (Yêu cầu đăng nhập)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]

    def get_queryset(self):
        return Review.objects.filter(booking__customer=self.request.user)






# Viewset của Booking (Yêu cầu phải đăng nhập)
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Yêu cầu OAuth2 Token
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_date']
    search_fields = ['customer__username']

    def get_queryset(self):
        user = self.request.user
        # LOGIC PHÂN QUYỀN: Nếu là Nhân viên/Quản lý thì được xem TẤT CẢ các đơn đặt phòng để làm thủ tục
        if user.role in ['RECEPTIONIST', 'ACCOUNTANT', 'MANAGER']:
            return Booking.objects.all()
        # LOGIC QUAN TRỌNG: Khách hàng nào chỉ thấy booking của người đó
        return Booking.objects.filter(customer=user)

    # Thêm action tùy chỉnh để khách hàng hủy phòng
    @action(methods=['post'], detail=True, url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.save()
            return Response({"message": "Hủy phòng thành công!"}, status=status.HTTP_200_OK)
        return Response({"error": "Không thể hủy phòng ở trạng thái này."}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['post'], detail=True, url_path='check-in')
    def check_in(self, request, pk=None):
        if request.user.role not in ['RECEPTIONIST', 'MANAGER']:
            return Response({"error": "Bạn không có quyền thực hiện check-in!"}, status=status.HTTP_403_FORBIDDEN)

        booking = self.get_object()

        if booking.status != 'CONFIRMED':
            return Response({"error": "Đơn đặt phòng này chưa được xác nhận thanh toán hoặc đã xử lý rồi!"},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'CHECKED_IN'
        booking.save()

        booking_details = booking.details.all()
        for detail in booking_details:
            room = detail.room
            room.status = 'OCCUPIED'
            room.save()

        return Response({
                            "message": f"Check-in thành công đơn hàng #{booking.id}. Các phòng liên quan đã chuyển sang ĐANG CÓ KHÁCH."},
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='check-out')
    def check_out(self, request, pk=None):
        if request.user.role not in ['RECEPTIONIST', 'MANAGER']:
            return Response({"error": "Bạn không có quyền thực hiện check-out!"}, status=status.HTTP_403_FORBIDDEN)

        booking = self.get_object()

        if booking.status != 'CHECKED_IN':
            return Response({"error": "Đơn đặt phòng này chưa thực hiện thủ tục check-in!"},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'CHECKED_OUT'
        booking.save()

        booking_details = booking.details.all()
        for detail in booking_details:
            room = detail.room
            room.status = 'CLEANING'
            room.save()

        return Response({
                            "message": f"Check-out thành công đơn hàng #{booking.id}. Các phòng liên quan đã chuyển sang ĐANG DỌN DẸP."},
                        status=status.HTTP_200_OK)


    #     roomtype_id = self.request.query_params.get('roomtype_id')
    #     if roomtype_id:
    #         query = query.filter(roomtype_id=roomtype_id)
    #     return query
    #
    # # Cách 2 để lọc
    # filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    # search_fields = ['room_number']
    # ordering_fields = ['roomtype_id']