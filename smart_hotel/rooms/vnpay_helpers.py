import hashlib
import hmac
import urllib.parse
from django.conf import settings
from datetime import datetime


class VNPayHelper:
    @staticmethod
    def get_payment_url(booking_id, amount, order_desc, ip_address):
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': settings.VNPAY_TMN_CODE,
            'vnp_Amount': int(amount * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': str(booking_id),
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
            'vnp_IpAddr': ip_address,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }

        sorted_params = sorted(vnp_params.items())
        query_string = urllib.parse.urlencode(sorted_params)

        hash_secret = settings.VNPAY_HASH_SECRET
        vnp_secure_hash = hmac.new(
            hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return f"{settings.VNPAY_URL}?{query_string}&vnp_SecureHash={vnp_secure_hash}"

    @staticmethod
    def validate_response(query_params):
        vnp_secure_hash = query_params.get('vnp_SecureHash')

        params = {k: v for k, v in query_params.items() if k not in ['vnp_SecureHash', 'vnp_SecureHashType']}
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)

        hash_secret = settings.VNPAY_HASH_SECRET
        calculated_hash = hmac.new(
            hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return calculated_hash == vnp_secure_hash