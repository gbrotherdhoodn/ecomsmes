from django.db import models
from decimal import Decimal as D
from oscar.apps.voucher.abstract_models import AbstractVoucher
from django.utils.translation import ugettext_lazy as _

ALL_SHIPPING_METHOD = 'all-shipping-method'
PERSONAL_COURIER_CODE = 'personal-courier'
KGX_COURIER_CODE = 'kgx-courier'


class Voucher(AbstractVoucher):
    min_odr_amount = models.DecimalField(decimal_places=2, max_digits=20,
                                         default=D('0.00'), verbose_name=_("Minimal Order Amount"))

    shipping_method = models.CharField(max_length=30, default=0,
                                       verbose_name=_("Courier Method"))

from oscar.apps.voucher.models import *  # noqa isort:skip
