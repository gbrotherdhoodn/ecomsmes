import http
import json
import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, QueryDict
from django.template.loader import render_to_string
from oscar.core.loading import get_model, get_class

from apps.payment.gateway import ApiClient
from apps.payment.constants import SETTLEMENT, PAID, BANK_TRANSFER, MANDIRI, PERMATA, CANCELED, \
    CREDIT_CARD

from apps.order.models import PaymentEvent, PaymentEventQuantity, PaymentEventType, bank_name_from_mask

log = logging.getLogger('smesco')

Source = get_model('payment', 'Source')

PaymentTransaction = get_model('payment', 'Transaction')
EventHandler = get_class('order.processing', 'EventHandler')


def build_message(order_data: dict):
    if order_data.get("payment_type") == BANK_TRANSFER:
        if order_data.get("va_numbers"):
            bank = order_data.get("va_numbers")[0].get("bank").upper()
            va_number = order_data.get("va_numbers")[0].get("va_number")
        elif order_data.get("permata_va_number"):
            bank = PERMATA.upper()
            va_number = order_data.get("permata_va_number")
        return f"Bank Name: {bank}, VA Number : {va_number}"

    elif order_data.get("payment_type") == MANDIRI:
        bank = "mandiri"
        biller_code = order_data.get("biller_code")
        va_number = order_data.get("bill_key")
        return f"Bank Name: {bank}, Biller Code: {biller_code},  VA Number : {va_number}"

    elif order_data.get("payment_type") == CREDIT_CARD:
        masked_card = bank_name_from_mask(order_data.get("masked_card"))
        card_type = order_data.get("card_type")
        status = order_data.get("channel_response_message")
        return f"{masked_card.bank_name} {card_type.title()} Card({masked_card.card_type}), Status: {status}"


def get_source(order):
    return Source.objects.get(order=order)


def midtrans_order_exist(request):
    client = ApiClient(settings.MIDTRANS.get("SERVER_KEY"), settings.MIDTRANS.get("SANDBOX"))
    body = json.loads(request.body)
    order_exist = client.get_order_status(body.get('order_id'))

    if order_exist.get("payment_type") == CREDIT_CARD:
        return order_exist

    if body.get('transaction_status') != order_exist.get('transaction_status'):
        return JsonResponse({"messages": "OK!"}, status=http.HTTPStatus.OK)

    return order_exist


def create_order_event(order, order_exist, expired=False):
    event_type, __ = PaymentEventType.objects.get_or_create(
        name=order_exist.get('transaction_status'))

    event = PaymentEvent.objects.create(
        order=order,
        event_type=event_type, amount=order_exist.get('gross_amount'),
        reference=order_exist.get('transaction_id'))

    for line in order.lines.all():
        PaymentEventQuantity.objects.create(
            event=event, line=line, quantity=line.quantity)

        if expired:
            line.stockrecord.cancel_allocation(line.quantity)
    log.info(f"finish create order event for {order}")


def create_order_notes(order, order_exist, expired=False):
    status = CANCELED.title() if expired else order_exist.get('transaction_status').title()
    order.notes.create(
        message=f"{build_message(order_exist)} And {status}", note_type="System",
        user=order.user)


def process_not_found_order(order, **kwargs):
    # we just send OK if not on SANDBOX MODE
    if settings.MIDTRANS.get("SANDBOX"):
        message = f"Order invalid, order number: {order.number} "
        return JsonResponse({"message": message}, status=http.HTTPStatus.NOT_FOUND)
    return JsonResponse({"message": "OK"}, status=http.HTTPStatus.OK)


def create_payment_transaction(order, source, order_exist):
    transaction = PaymentTransaction.objects.create(source=source, amount=order_exist.get('gross_amount'))
    transaction.txn_type = order_exist.get('payment_type')
    transaction.reference = order_exist.get('transaction_id')
    if (order.status != PAID) and (order_exist.get('transaction_status') == SETTLEMENT):
        transaction.status = PAID
    else:
        transaction.status = order_exist.get('transaction_status')
    transaction.save()
    return transaction


def send_email_paid(order, **kwargs):
    current_site = get_current_site(kwargs.get('request'))

    mail_subject = f'Terima Kasih, Pembayaran Order {order.number} Berhasil'
    message_html = render_to_string('customer/emails/commtype_order_va_paid_body.html', {
        'user': order.user,
        'domain': current_site.domain,
        'order': order
    })

    message_text = render_to_string('customer/emails/commtype_order_va_paid_body.txt', {
        'user': order.user,
        'domain': current_site.domain,
        'order': order
    })
    to_email = order.user.email
    email = EmailMultiAlternatives(
        mail_subject, message_text, to=[to_email], from_email=settings.OSCAR_FROM_EMAIL
    )
    email.attach_alternative(message_html, 'text/html')
    email.send()
    log.info(f"Email for Order {order.order_number} was Sent")


def process_paid_order(order, **kwargs):
    """

    :param order: Order object
    :param kwargs:
    :return:
    """
    source = get_source(order)
    order_exist = midtrans_order_exist(kwargs.get("request"))

    if (order.status == PAID) and (order_exist.get('transaction_status') == SETTLEMENT):
        return JsonResponse({"message": "Already Paid"}, status=http.HTTPStatus.OK)

    create_payment_transaction(order, source, order_exist)

    order.set_status(PAID)
    source.amount_debited = order_exist.get('gross_amount')
    source.save()

    create_order_event(order, order_exist)

    create_order_notes(order, order_exist)

    if order_exist.get("payment_type") != CREDIT_CARD:
        send_email_paid(order, request=kwargs.get("request"))
    log.info(f"Order Id {order.order_number} has been Paid")
    return JsonResponse({"message": "Success"}, status=http.HTTPStatus.OK)


def process_placed_order(order, **kwargs):
    """

    :param order: Order object
    :param kwargs:
    :return:
    """
    if order.payment_events.filter(event_type__code="pending").count() > 2:
        return JsonResponse({"message": "Payment Pending"}, status=http.HTTPStatus.OK)

    source = get_source(order)
    order_exist = midtrans_order_exist(kwargs.get("request"))

    create_payment_transaction(order, source, order_exist)

    create_order_event(order, order_exist)

    create_order_notes(order, order_exist)
    log.info(f"Order Id {order.order_number} has been Placed by : System")
    return JsonResponse({"message": "Success"}, status=http.HTTPStatus.OK)


def process_expired_order(order, **kwargs):
    """

    :param order: Order object
    :param kwargs:
    :return:
    """
    order.set_status(CANCELED)
    source = get_source(order)
    order_exist = midtrans_order_exist(kwargs.get("request"))

    create_payment_transaction(order, source, order_exist)

    create_order_event(order, order_exist, expired=True)

    create_order_notes(order, order_exist, expired=True)
    log.info(f"Order Id {order.order_number} has been Cancelled by : System")

    return JsonResponse({"message": "Success"}, status=http.HTTPStatus.OK)


def process_cancel_order(request, order=False):
    client = ApiClient(settings.MIDTRANS.get("SERVER_KEY"), settings.MIDTRANS.get("SANDBOX"))
    order_id = order if order else QueryDict(request.body).get("order")
    response = client.cancel_payment(order_id)
    log.info(f"Order Id {order_id} has been Cancelled by : {request.user}")
    return response


def process_capture_order(order, **kwargs):
    """

    :param order:Order object
    :param kwargs:
    :return: JsonResponse
    """
    source = get_source(order)
    order_exist = midtrans_order_exist(kwargs.get("request"))

    if (order.status == PAID) and (order_exist.get('transaction_status') == SETTLEMENT):
        return JsonResponse({"message": "Already Paid"}, status=http.HTTPStatus.OK)

    create_payment_transaction(order, source, order_exist)

    order.set_status(PAID)
    source.amount_debited = order_exist.get('gross_amount')
    source.save()

    create_order_event(order, order_exist)

    create_order_notes(order, order_exist)

    send_email_paid(order, request=kwargs.get("request"))
    log.info(f"process capture payment for order {order.order_number} Success")

    return JsonResponse({"message": "Success"}, status=http.HTTPStatus.OK)
