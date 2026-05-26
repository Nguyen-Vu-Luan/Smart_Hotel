from rest_framework import viewsets, generics, filters, status, parsers, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import RoomType, Room, User, Service, Booking, BookingService, Payment, Review
from rooms import serializers, paginators
from rest_framework.decorators import action
from rest_framework.response import Response
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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['-created_date']

    def get_queryset(self):
        # LOGIC QUAN TRỌNG: Khách hàng nào chỉ thấy booking của người đó
        return Booking.objects.filter(customer=self.request.user)

    # Thêm action tùy chỉnh để khách hàng hủy phòng
    @action(methods=['post'], detail=True, url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'PENDING':
            booking.status = 'CANCELLED'
            booking.save()
            return Response({"message": "Hủy phòng thành công!"})
        return Response({"error": "Không thể hủy phòng ở trạng thái này."}, status=400)
        roomtype_id = self.request.query_params.get('roomtype_id')
        if roomtype_id:
            query = query.filter(roomtype_id=roomtype_id)
        return query

    # Cách 2 để lọc
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['room_number']
    ordering_fields = ['roomtype_id']