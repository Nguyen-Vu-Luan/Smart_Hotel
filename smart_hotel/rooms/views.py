from rest_framework import viewsets, generics, filters, status, parsers, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import RoomType, Room, User, Service, Booking, BookingService, Payment, Review, BookingDetail
from rooms import serializers, paginators
from rest_framework.decorators import action
from rest_framework.response import Response
from rooms.vnpay_helpers import VNPayHelper
from .utils import send_invoice_email
from .perms import IsReviewOwner
from django.db.models import Sum, Count, Avg
from django.db.models.functions import ExtractMonth
from datetime import datetime



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



    @action(methods=['get'], detail=False, url_path='search-rooms', permission_classes=[permissions.AllowAny])
    def search_rooms(self, request):
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        room_type_id = request.query_params.get('room_type_id')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        rooms = Room.objects.filter(active=True)

        if check_in_str and check_out_str:
            try:
                check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

                if check_in >= check_out:
                    return Response({"error": "Ngày nhận phòng phải nhỏ hơn ngày trả phòng!"},
                                    status=status.HTTP_400_BAD_REQUEST)

                intersecting_bookings = Booking.objects.filter(
                    status__in=['CONFIRMED', 'CHECKED_IN'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                )

                booked_room_ids = BookingDetail.objects.filter(
                    booking__in=intersecting_bookings
                ).values_list('room_id', flat=True)

                rooms = rooms.exclude(id__in=booked_room_ids)

            except ValueError:
                return Response({"error": "Định dạng ngày không hợp lệ. Vui lòng dùng YYYY-MM-DD"},
                                status=status.HTTP_400_BAD_REQUEST)

        if room_type_id:
            rooms = rooms.filter(room_type_id=room_type_id)

        if min_price:
            rooms = rooms.filter(room_type__base_price__gte=float(min_price))
        if max_price:
            rooms = rooms.filter(room_type__base_price__lte=float(max_price))

        page = self.paginate_queryset(rooms)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
    # permission_classes = [permissions.AllowAny]

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

        # # 🚀 XỬ LÝ LẤY USER ANONYMOUS ĐỂ TEST KHÔNG CẦN TOKEN ĐĂNG NHẬP
        # user = request.user
        # if user.is_anonymous:
        #     user = User.objects.first()  # Bốc đại user đầu tiên trong DB giống y như bên Serializer
        #
        # try:
        #     # Thay request.user bằng biến user đã được xử lý ở trên
        #     booking = Booking.objects.get(id=booking_id, customer=user)
        # except Booking.DoesNotExist:
        #     return Response({"error": "Đơn đặt phòng không tồn tại hoặc không thuộc quyền sở hữu của bạn!"},
        #                     status=status.HTTP_404_NOT_FOUND)

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
    # permission_classes = [permissions.AllowAny]
    permission_classes = [permissions.IsAuthenticated]# Yêu cầu OAuth2 Token
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



class ManagerReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # return [permissions.AllowAny()]
        return super().get_permissions()

    def check_manager_permission(self, request):
        if request.user.is_anonymous or request.user.role != 'MANAGER':
            return False
        return True

    @action(methods=['get'], detail=False, url_path='revenue')
    def get_revenue_report(self, request):
        if not self.check_manager_permission(request):
            return Response({"error": "Bạn không có quyền MANAGER để xem báo cáo doanh thu!"},
                            status=status.HTTP_403_FORBIDDEN)

        current_year = datetime.now().year
        year = request.query_params.get('year', current_year)
        try:
            year = int(year)
        except ValueError:
            year = current_year

        room_payments = Payment.objects.filter(
            payment_status='SUCCESS',
            created_date__year=year
        ).annotate(
            month=ExtractMonth('created_date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        service_payments = BookingService.objects.filter(
            booking__status__in=['CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT'],
            created_date__year=year
        ).annotate(
            month=ExtractMonth('created_date')
        ).values('month').annotate(
            total=Sum('total_price')
        ).order_by('month')

        monthly_data = {m: {"room_revenue": 0, "service_revenue": 0, "total_revenue": 0} for m in range(1, 13)}

        for p in room_payments:
            m = p['month']
            monthly_data[m]["room_revenue"] = float(p['total'] or 0)
            monthly_data[m]["total_revenue"] += float(p['total'] or 0)

        for s in service_payments:
            m = s['month']
            monthly_data[m]["service_revenue"] = float(s['total'] or 0)
            monthly_data[m]["total_revenue"] += float(s['total'] or 0)

        quarter_data = {1: 0, 2: 0, 3: 0, 4: 0}
        total_year_revenue = 0

        for month, revenue in monthly_data.items():
            total_month = revenue["total_revenue"]
            total_year_revenue += total_month

            if month in [1, 2, 3]:
                quarter_data[1] += total_month
            elif month in [4, 5, 6]:
                quarter_data[2] += total_month
            elif month in [7, 8, 9]:
                quarter_data[3] += total_month
            elif month in [10, 11, 12]:
                quarter_data[4] += total_month

        report_by_month = [{"month": m, **data} for m, data in monthly_data.items()]

        return Response({
            "year": year,
            "total_year_revenue": round(total_year_revenue, 2),
            "revenue_by_quarters": {f"Quý {q}": round(val, 2) for q, val in quarter_data.items()},
            "revenue_by_months": report_by_month
        }, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='occupancy-rate')
    def get_occupancy_rate(self, request):
        if not self.check_manager_permission(request):
            return Response({"error": "Bạn không có quyền quản lý để xem mật độ phòng!"},
                            status=status.HTTP_403_FORBIDDEN)

        total_rooms_count = Room.objects.filter(active=True).count()
        if total_rooms_count == 0:
            return Response({"message": "Khách sạn chưa cấu hình phòng nào.", "occupancy_rate": 0},
                            status=status.HTTP_200_OK)

        occupied_rooms_count = Room.objects.filter(active=True, status='OCCUPIED').count()

        current_occupancy_rate = (occupied_rooms_count / total_rooms_count) * 100


        room_status_distribution = Room.objects.filter(active=True).values('status').annotate(
            quantity=Count('id')
        )

        popular_room_types = BookingDetail.objects.filter(
            booking__status__in=['CONFIRMED', 'CHECKED_IN']
        ).values('room__room_type__name').annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')

        return Response({
            "total_rooms": total_rooms_count,
            "occupied_rooms": occupied_rooms_count,
            "current_occupancy_rate_percentage": round(current_occupancy_rate, 2),
            "room_status_distribution": list(room_status_distribution),
            "popular_room_types": list(popular_room_types)
        }, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='customer-feedback')
    def get_customer_feedback(self, request):
        if not self.check_manager_permission(request):
            return Response({"error": "Bạn không có quyền quản lý để xem đánh giá tổng hợp!"},
                            status=status.HTTP_403_FORBIDDEN)

        reviews_queryset = Review.objects.all()
        total_reviews = reviews_queryset.count()

        if total_reviews == 0:
            return Response({"message": "Chưa có phản hồi hay đánh giá nào từ khách hàng."},
                            status=status.HTTP_200_OK)

        average_stars = reviews_queryset.aggregate(avg_rating=Avg('rating'))['avg_rating']

        rating_distribution = reviews_queryset.values('rating').annotate(
            count=Count('id')
        ).order_by('-rating')

        bad_reviews = reviews_queryset.filter(rating__lte=2).order_by('-created_date')[:5]

        bad_reviews_details = [{
            "review_id": r.id,
            "booking_id": r.booking.id,
            "customer": r.booking.customer.username,
            "rating": r.rating,
            "comment": r.comment,
            "date": r.created_date.strftime("%d/%m/%Y")
        } for r in bad_reviews]

        return Response({
            "total_reviews_received": total_reviews,
            "hotel_average_rating": round(average_stars, 2),
            "rating_distribution": list(rating_distribution),
            "urgent_negative_reviews": bad_reviews_details
        }, status=status.HTTP_200_OK)