from __future__ import absolute_import

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from oscar.core.compat import get_user_model
from oscar.core.loading import get_model

from apps.customer.tokens import account_activation_token

import logging

from celery import task

User = get_user_model()
Order = get_model('order', 'Order')

logger = logging.getLogger(__name__)


@task(name='send_email')
def send_email(subject, to_email, message_html, message_text=None, from_email=settings.OSCAR_FROM_EMAIL):
    if not message_text:
        message_text = message_html
    email = EmailMultiAlternatives(
        subject, message_text, to=[to_email], from_email=from_email
    )
    email.attach_alternative(message_html, 'text/html')
    email.send()


@task(name='send_registration_email')
def send_registration_email(email, user_id, scheme, domain,):
    user = User.objects.get(pk=user_id)
    mail_subject = f"Silahkan aktivasi akun anda di {getattr(settings, 'OSCAR_SHOP_TAGLINE', None)}"
    message = render_to_string('customer/emails/commtype_account_verification_body.html', {
        'user': user,
        'scheme': scheme,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })
    to_email = email
    send_email.delay(mail_subject, to_email, message)


@task(name='send_registration_activation_email')
def send_registration_activation_email(user_id, domain):
    user = User.objects.get(pk=user_id)
    mail_subject = f"Akun Anda di {getattr(settings, 'OSCAR_SHOP_TAGLINE', None)} telah aktif"
    message = render_to_string('customer/emails/commtype_registration_body.html', {
        'user': user,
        'domain': domain,
    })
    to_email = user.email
    send_email.delay(mail_subject, to_email, message)


@task(name='send_reset_password_email')
def send_reset_password_email(user_id, domain, reset_url):
    user = User.objects.get(pk=user_id)
    email_subject = f"Atur ulang kata sandi Anda di {getattr(settings, 'OSCAR_SHOP_TAGLINE', None)}"
    message = render_to_string('customer/emails/commtype_password_reset_body.html', {
        'user': user,
        'domain': domain,
        'reset_url': reset_url
    })
    send_email.delay(email_subject, user.email, message)


@task(name='send_email_order')
def send_email_order(status, order_id, current_site=None):
    order = Order.objects.get(pk=order_id)
    mail_subject = ''
    filename = ''
    if status == getattr(settings, 'ORDER_STATUS_PLACED'):
        filename = 'placed'
        mail_subject = f'JimshoneyOfficial.com - Mohon Melakukan Pembayaran untuk Order {order.number}'
    elif status == getattr(settings, 'ORDER_STATUS_CANCELED'):
        filename = 'canceled'
        mail_subject = f'JimshoneyOfficial.com - Pesanan {order.number} Telah Dibatalkan'
    elif status == getattr(settings, 'ORDER_STATUS_PAID'):
        filename = 'va_paid'
        mail_subject = f'JimshoneyOfficial.com - Terima Kasih, Pembayaran Order #{order.number} Berhasil'
    elif status == getattr(settings, 'ORDER_STATUS_COMPLETED'):
        filename = 'completed'
        mail_subject = f'JimshoneyOfficial.com - Pesanan {order.number} Telah Selesai'
    elif status == getattr(settings, 'ORDER_STATUS_SHIPPED'):
        filename = 'shipped'
        mail_subject = f'JimshoneyOfficial.com - Pesanan {order.number} Telah Dikirim'

    if not mail_subject and not filename:
        return

    if not current_site:
        current_site = Site.objects.last().domain

    message_html = render_to_string(f'customer/emails/commtype_order_{filename}_body.html', {
        'user': order.user,
        'order': order,
        'domain': current_site
    })
    message_text = render_to_string(f'customer/emails/commtype_order_{filename}_body.txt', {
        'user': order.user,
        'order': order,
        'domain': current_site
    })

    to_email = order.user.email
    send_email.delay(mail_subject, to_email, message_html, message_text)
