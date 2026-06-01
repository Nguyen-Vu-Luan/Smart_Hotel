from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth, ExtractQuarter
from .models import Payment, Room, Review



def send_invoice_email(booking):

    customer = booking.customer
    if not customer.email:
        print(f"Không thể gửi mail cho Booking #{booking.id} vì tài khoản {customer.username} không có email.")
        return False

    subject = f"[Smart Hotel] Hóa Đơn Điện Tử - Đơn Đặt Phòng #{booking.id}"

    raw_details = booking.details.all()

    unique_details = {d.room.id: d for d in raw_details}.values()
    booking_details = list(unique_details)
    booking_services = booking.services.all()

    context = {
        'customer_name': customer.get_full_name() or customer.username,
        'booking': booking,
        'details': booking_details,
        'booking_services': booking_services,
    }

    text_content = f"Cảm ơn bạn đã thanh toán thành công đơn hàng #{booking.id}. Tổng tiền: {booking.total_amount} VND."

    html_content = render_to_string('emails/invoice_template.html', context)

    try:
        msg = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer.email]
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        print(f"Đã gửi email hóa đơn thành công tới {customer.email}!")
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {str(e)}")
        return False


def get_stats_data(period, year):
    qs = Payment.objects.filter(payment_status='SUCCESS', created_date__year=year)

    if period == 'quarter':
        data = qs.annotate(time=ExtractQuarter('created_date')).values('time') \
            .annotate(total=Sum('amount')).order_by('time')
        labels = ['Quý 1', 'Quý 2', 'Quý 3', 'Quý 4']
        values = [0] * 4
    else:
        data = qs.annotate(time=ExtractMonth('created_date')).values('time') \
            .annotate(total=Sum('amount')).order_by('time')
        labels = [f"T{i}" for i in range(1, 13)]
        values = [0] * 12

    for item in data:
        values[item['time'] - 1] = float(item['total'] or 0)

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='OCCUPIED').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    avg_rating = Review.objects.aggregate(avg=Sum('rating') / Count('id'))['avg'] or 0

    return {
        'labels': labels, 'values': values,
        'occupancy_rate': round(occupancy_rate, 2),
        'avg_rating': round(avg_rating, 2)
    }