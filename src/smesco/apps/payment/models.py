from oscar.apps.payment.abstract_models import AbstractSourceType, AbstractSource
from django.utils.translation import ugettext_lazy as _
from django.db import models


class SourceTypeQuerySet(models.QuerySet):

    def by_source_type(self, source_type):
        return self.filter(source_type=source_type).distinct('code')

    def image_by_source_type(self, source_type):
        return self.filter(source_type=source_type).values_list('image', flat=True)

    def source_type_available(self):
        return self.all().distinct('source_type').values_list('source_type', flat=True)


class SourceTypeManager(models.Manager):

    def get_queryset(self):
        return SourceTypeQuerySet(self.model).filter(is_active=True)


class SourceType(AbstractSourceType):
    image = models.ImageField(_("Bank Image"), blank=True, null=True)
    source_type = models.CharField(_("Payment Method"), blank=True, null=True, max_length=32)
    is_active = models.BooleanField(_("Is Payment Available?"), default=True)
    code = models.CharField(_("Bank Code"), max_length=32)
    percent_fee = models.DecimalField(_("Percent Fee"), max_digits=3, default=0, decimal_places=2)
    bank_fee = models.DecimalField(_("Bank Fee"), max_digits=11, default=0, decimal_places=2)
    amount_fee = models.DecimalField(_("Amount Fee"), max_digits=11, default=0, decimal_places=2)

    objects = SourceTypeManager()


class Source(AbstractSource):
    PAYMENT_SUCCESS = '1'
    PAYMENT_FAIL = '0'
    PAYMENT_PENDING = '6'
    PAYMENT_INITIATE = '99'
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_SUCCESS, 'Payment Success'),
        (PAYMENT_FAIL, 'Payment Failed'),
        (PAYMENT_PENDING, 'Payment Pending'),
        (PAYMENT_INITIATE, 'Payment Initiated'),
    )
    va_number = models.CharField(_("Virtual Account Number"), blank=True, null=True, max_length=32)
    va_expired = models.DateTimeField(_("Virtual Account Expired Date"), blank=True, null=True)
    payment_status = models.CharField('Payment Status', max_length=2, choices=PAYMENT_STATUS_CHOICES,
                                      default=PAYMENT_INITIATE)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Created"), auto_now=True)

from oscar.apps.payment.models import *  # noqa isort:skip

