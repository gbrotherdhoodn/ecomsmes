from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model
from oscar.apps.dashboard.vouchers.forms import VoucherForm as CoreVoucherForm
from apps.voucher.models import KGX_COURIER_CODE

Benefit = get_model('offer', 'Benefit')
RangeDestination = get_model('offer', 'RangeDestination')


class VoucherForm(CoreVoucherForm):

    min_odr_amount = forms.DecimalField(initial=0, label=_("Minimum Order Amount"))
    destination_range = forms.ModelChoiceField(
        required=False,
        label=_("Destination Range"),
        queryset=RangeDestination.objects.all()
    )

    TYPE_SHIP = (
        (KGX_COURIER_CODE, _('KGX Kurir')),
    )

    shipping_method = forms.ChoiceField(
        choices=TYPE_SHIP,
        label=_("Courier Method"),
    )
