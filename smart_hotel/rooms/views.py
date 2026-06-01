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
from django.db import transaction


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



class RoomTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = RoomType.objects.filter(active=True)
    serializer_class = serializers.RoomTypeSerializer

    @action(methods=['get'], detail=True, url_path='reviews', permission_classes=[permissions.AllowAny])
    def get_reviews(self, request, pk=None):
        room_type = self.get_object()

        reviews = Review.objects.filter(
            booking__details__room__room_type=room_type
        ).distinct()

        serializer = serializers.PublicReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class RoomViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Room.objects.filter(active=True)
    serializer_class = serializers.RoomSerializer
    pagination_class = paginators.ItemPaginator

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['room_type', 'status']
    search_fields = ['room_number']
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


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(active=True)
    serializer_class = serializers.ServiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class BookingServiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookingServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingService.objects.filter(booking__customer=self.request.user)


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
            return Response({"error": "Đơn đặt phòng không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)

        details = booking.details.all()
        room_price = details[0].price_at_booking if details.exists() else 0
        service_price = booking.services.aggregate(total=Sum('total_price'))['total'] or 0

        final_amount = room_price + service_price

        booking.total_amount = final_amount
        booking.save()

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        payment, created = Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'amount': final_amount,
                'payment_method': 'E_WALLET',
                'payment_status': 'PENDING'
            }
        )

        payment_url = VNPayHelper.get_payment_url(
            booking_id=booking.id,
            amount=int(final_amount),
            order_desc=f"Thanh toan don #{booking.id}",
            ip_address=ip_address
        )

        return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='vnpay-callback', permission_classes=[permissions.AllowAny])
    def vnpay_callback(self, request):
        query_params = request.GET.dict()

        if VNPayHelper.validate_response(query_params):
            txn_ref = query_params.get('vnp_TxnRef')
            booking_id = txn_ref.split('_')[0]
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
                'payment_method': 'CASH',
                'payment_status': 'SUCCESS'
            }
        )

        booking.status = 'CONFIRMED'
        booking.save()

        send_invoice_email(booking)

        return Response({"message": "Nhân viên đã xác nhận thanh toán tiền mặt thành công!"},
                        status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]

    def get_queryset(self):
        return Review.objects.filter(booking__customer=self.request.user)



class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_date']
    search_fields = ['customer__username']


    def perform_create(self, serializer):
        check_in_str = self.request.data.get('check_in_date')
        check_out_str = self.request.data.get('check_out_date')

        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

        details_data = self.request.data.get('details', [])
        services_data = self.request.data.get('services', [])

        if not details_data:
            raise ValidationError({"details": "Vui lòng chọn ít nhất một phòng."})

        room_id = details_data[0].get('room')
        room = Room.objects.get(pk=room_id)


        overlapping = Booking.objects.filter(
            details__room_id=room_id,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        ).exclude(status__in=['CANCELLED', 'CHECKED_OUT'])


        if overlapping.exists():
            raise ValidationError({"error": f"Phòng {room.room_number} đã bị đặt trong khoảng thời gian này!"})


        days = (check_out - check_in).days
        if days <= 0:
            raise ValidationError({"error": "Ngày trả phòng phải sau ngày nhận phòng."})

        total_room_price = room.room_type.base_price * days
        total_service_price = 0
        for s in services_data:
            if isinstance(s, dict):
                s_id = s.get('service_id')
                qty = s.get('quantity', 1)
            else:
                s_id = s
                qty = 1

            service = Service.objects.get(pk=s_id)
            total_service_price += (service.price * qty)


        with transaction.atomic():
            booking = serializer.save(
                customer=self.request.user,
                status='PENDING',
                total_amount=total_room_price + total_service_price,
                check_in_date=check_in,
                check_out_date=check_out
            )


            if not BookingDetail.objects.filter(booking=booking, room=room).exists():
                BookingDetail.objects.create(
                    booking=booking,
                    room=room,
                    price_at_booking=room.room_type.base_price
                )


            for s in services_data:
                if isinstance(s, dict):
                    s_id = s.get('service_id')
                    qty = s.get('quantity', 1)
                else:
                    s_id = s
                    qty = 1

                service = Service.objects.get(pk=s_id)
                BookingService.objects.create(
                    booking=booking,
                    service=service,
                    quantity=qty,
                    total_price=service.price * qty
                )

    @action(methods=['post'], detail=True, url_path='confirm-cod')
    def confirm_cod(self, request, pk=None):
        booking = self.get_object()

        if booking.status != 'PENDING':
            return Response({"error": "Đơn hàng không hợp lệ hoặc đã được xác nhận trước đó."},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'CONFIRMED'
        booking.save()

        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'payment_method': 'CASH',  
                'payment_status': 'PENDING'
            }
        )

        return Response({"message": "Đặt phòng thành công, vui lòng thanh toán tại quầy khi nhận phòng!"},
                        status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        if user.role in ['RECEPTIONIST', 'ACCOUNTANT', 'MANAGER']:
            return Booking.objects.all()
        return Booking.objects.filter(customer=user)

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




