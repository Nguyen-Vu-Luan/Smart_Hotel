from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_invoice_email(booking):

    customer = booking.customer
    if not customer.email:
        print(f"Không thể gửi mail cho Booking #{booking.id} vì tài khoản {customer.username} không có email.")
        return False

    subject = f"[Smart Hotel] Hóa Đơn Điện Tử - Đơn Đặt Phòng #{booking.id}"

    booking_details = booking.details.all()

    context = {
        'customer_name': customer.get_full_name() or customer.username,
        'booking': booking,
        'details': booking_details,
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