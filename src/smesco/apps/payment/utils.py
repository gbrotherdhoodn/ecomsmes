import logging
import hashlib
import binascii
import base64

from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site

from apps.payment.helpers import process_paid_order, process_placed_order, process_not_found_order, \
    process_expired_order
from apps.payment.constants import NOT_FOUND, PENDING, SETTLEMENT, EXPIRED, CAPTURE
from oscar.core.loading import get_class, get_model
from django.db import transaction as trans

OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')
OrderEventHandler = get_class('order.processing', 'EventHandler')

Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
OrderNote = get_model('order', 'OrderNote')


log = logging.getLogger('smesco')


process_order = {
    SETTLEMENT: process_paid_order,
    PENDING: process_placed_order,
    NOT_FOUND: process_not_found_order,
    EXPIRED: process_expired_order,
    CAPTURE: process_paid_order
}


def ipay_signature_creator(order_number, total_order):
    """
    :param order_number:
    :param total_order:
    :return: signature key
    """
    merchant_key = getattr(settings, 'IPAY_MERCHANT_KEY', '')
    merchant_code = getattr(settings, 'IPAY_MERCHANT_CODE', '')
    ref_no = order_number
    amount = int(total_order)
    currency = getattr(settings, 'OSCAR_DEFAULT_CURRENCY')

    string_key = f'{merchant_key}{merchant_code}{ref_no}{amount}00{currency}'
    encode_key = string_key.encode('utf-8')
    hash_key = hashlib.sha1(encode_key).hexdigest()
    hextodig_key = binascii.unhexlify(hash_key)
    return base64.b64encode(hextodig_key).decode("utf-8")


def ipay_signature_creator_response(payment_id, order_number, total_order, status, xfield):
    """
    :param payment_id:
    :param order_number:
    :param total_order:
    :param status:
    :param xfield:
    :return: signature key
    """
    merchant_key = getattr(settings, 'IPAY_MERCHANT_KEY', '')
    merchant_code = getattr(settings, 'IPAY_MERCHANT_CODE', '')
    ref_no = order_number
    amount = int(total_order)
    currency = getattr(settings, 'OSCAR_DEFAULT_CURRENCY')

    string_key = f'{merchant_key}{merchant_code}{payment_id}{ref_no}{amount}00{currency}{status}{xfield}'
    encode_key = string_key.encode('utf-8')
    hash_key = hashlib.sha1(encode_key).hexdigest()
    hextodig_key = binascii.unhexlify(hash_key)
    return base64.b64encode(hextodig_key).decode("utf-8")


def get_complete_url(request, url, order_number, next=None):
    site = get_current_site(request)

    complete_url = "%s://%s%s" % (
                    request.scheme,
                    site.domain,
                    reverse_lazy(url, args=(),
                                 kwargs={'order_number': order_number}))

    if next:
        complete_url = "%s?next=%s" % (complete_url, reverse_lazy(next, args=(),
                                       kwargs={'order_number': order_number}))
    return complete_url


class PaymentServices(OrderPlacementMixin):

    def handle_payment(self, order, transaction_id, user=None):
        if not user:
            user = order.user
        total_incl_tax = order.total_incl_tax
        # Payment successful! Record payment source
        log.info(f'Payment Order {order.number} initiated handle payment')

        try:
            self.add_payment_event('payment', total_incl_tax)
            log.info(f'Payment Order {order.number} success add payment_event')
            order.refresh_from_db()
            source = order.sources.last()
            if source:
                source.debit(amount=None,
                             reference=transaction_id,
                             status='Close Payment')
                log.info(f'Payment Order {order.number} success create transactions')
            # self.change_order_status(order, user, 'Paid')
            log.info(f'Payment Order {order.number} success change to paid')
            handler = OrderEventHandler(user)
            handler.consume_stock_allocations(order)
            handler.handle_order_status_change(order, 'Paid')
            log.info(f'Payment Order {order.number} consume allocation stocks')
        except Exception as e:
            log.error(f"erorr {e}")

    def payment_receive_services(self, order, **cleaned_data):
        signature = cleaned_data.get('Signature', '')
        status = cleaned_data.get('Status', '')
        va = cleaned_data.get('VirtualAccountAssigned', '')
        va_expired = cleaned_data.get('ETransactionExpiryDate', '')
        payment_id = cleaned_data.get('PaymentId', '')
        xfield = cleaned_data.get('xfield1', '')
        payment_source = order.sources.last()
        msg = ''
        success = False
        if signature != ipay_signature_creator_response(payment_id, order.number, order.total_incl_tax, status, xfield):
            log.warning(f'Signature not match for order {order.number}')
            msg = ('Maaf, Terdapat Kendala saat melakukan pembayaran.'
                   ' Mohon untuk mengulangi proses pembayaran')

        if status == Source.PAYMENT_FAIL:
            log.error(f"Payment for Order {order.number} failed")
            payment_source.payment_status = Source.PAYMENT_FAIL
            payment_source.save()
            error = cleaned_data.get('ErrDesc', None)
            if error:
                log.error(f"Payment Error detail from IPAY {error}")
            msg = ('Maaf, Terdapat Kendala saat melakukan pembayaran.'
                   ' Mohon untuk mengulangi proses pembayaran')

        if status == Source.PAYMENT_PENDING:
            payment_source.payment_status = Source.PAYMENT_PENDING
            if not payment_source.va_number and va:
                payment_source.va_number = va
                if va_expired:
                    payment_source.va_expired = va_expired
                log.info(f"Set Payment VA {order.number}")
            payment_source.save()
            success = True
            log.info(f"Payment for order {order.number} was pending")

        log.info(f"Payment for order {order.number} success set as {payment_source.payment_status}")
        if status == Source.PAYMENT_SUCCESS and payment_source.payment_status != Source.PAYMENT_SUCCESS:
            with trans.atomic():
                log.info(f"prepare to set status success")
                ps = Source.objects.select_for_update().get(pk=payment_source.id)
                ps.payment_status = Source.PAYMENT_SUCCESS
                ps.save()
                log.info(f"Payment flaging to success done for order {order.number}")
                self.handle_payment(order, cleaned_data.get('TransId', None), order.user)
                log.info(f"Payment Success for order {order.number}")
            msg = 'Selamat, Pembayaran Anda berhasil !'
            success = True

        payment_source.refresh_from_db()
        if payment_source.payment_status == Source.PAYMENT_SUCCESS:
            success = True
        log.info(f"status handle payment {success} with message {msg}")
        return success, msg

