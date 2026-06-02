from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from rooms.models import Booking
from django.utils import timezone
from datetime import date
import time

def cleanup_expired_bookings():
    expired = Booking.objects.filter(status='PENDING', expired_at__lt=timezone.now())
    for b in expired:
        b.status = 'CANCELLED'
        b.save()
        print(f"Đã tự động hủy đơn #{b.id}")

    today = date.today()
    expired_no_shows = Booking.objects.filter(
        status='CONFIRMED',
        check_in_date__lt=today,
        payments__payment_status='PENDING',
        payments__payment_method='CASH'
    )

    for b in expired_no_shows:
        b.status = 'CANCELLED'
        b.save()

        payment = b.payments.filter(payment_status='PENDING').first()
        if payment:
            payment.payment_status = 'FAILED'
            payment.save()

        print(f"Đã hủy đơn no-show #{b.id}")

class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_job(cleanup_expired_bookings, 'interval', seconds=60)
        scheduler.start()
        try:
            while True: time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()