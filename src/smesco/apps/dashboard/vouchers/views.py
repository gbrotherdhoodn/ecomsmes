from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class, get_model
from oscar.apps.dashboard.vouchers.views import VoucherCreateView as VoucherCreateViewCustom, \
    VoucherUpdateView as VoucherUpdateViewCustom, VoucherDeleteView as VoucherDeleteViewCustom

VoucherForm = get_class('dashboard.vouchers.forms', 'VoucherForm')
Voucher = get_model('voucher', 'Voucher')
ConditionalOffer = get_model('offer', 'ConditionalOffer')
Benefit = get_model('offer', 'Benefit')
Condition = get_model('offer', 'Condition')


class VoucherCreateView(VoucherCreateViewCustom):

    @transaction.atomic()
    def form_valid(self, form):
        # Create offer and benefit
        condition = Condition.objects.create(
            range=form.cleaned_data['benefit_range'],
            type=Condition.COUNT,
            value=1,
            range_destination=form.cleaned_data['destination_range']
        )
        benefit = Benefit.objects.create(
            range=form.cleaned_data['benefit_range'],
            type=form.cleaned_data['benefit_type'],
            value=form.cleaned_data['benefit_value']
        )
        name = form.cleaned_data['name']
        offer = ConditionalOffer.objects.create(
            name=_("Offer for voucher '%s'") % name,
            offer_type=ConditionalOffer.VOUCHER,
            benefit=benefit,
            condition=condition,
            exclusive=form.cleaned_data['exclusive'],
        )
        voucher = Voucher.objects.create(
            name=name,
            code=form.cleaned_data['code'],
            usage=form.cleaned_data['usage'],
            start_datetime=form.cleaned_data['start_datetime'],
            end_datetime=form.cleaned_data['end_datetime'],
            min_odr_amount=form.cleaned_data['min_odr_amount'],
            shipping_method=form.cleaned_data['shipping_method'],
        )
        voucher.offers.add(offer)
        return HttpResponseRedirect(self.get_success_url())


class VoucherUpdateView(VoucherUpdateViewCustom):

    def get_initial(self):
        voucher = self.get_voucher()
        offer = voucher.offers.all()[0]
        benefit = offer.benefit
        return {
            'name': voucher.name,
            'code': voucher.code,
            'start_datetime': voucher.start_datetime,
            'end_datetime': voucher.end_datetime,
            'usage': voucher.usage,
            'benefit_type': benefit.type,
            'benefit_range': benefit.range,
            'benefit_value': benefit.value,
            'exclusive': offer.exclusive,
            'min_odr_amount': voucher.min_odr_amount,
            'shipping_method': voucher.shipping_method,
            'destination_range': offer.condition.range_destination,
        }

    @transaction.atomic()
    def form_valid(self, form):
        voucher = self.get_voucher()
        voucher.name = form.cleaned_data['name']
        voucher.code = form.cleaned_data['code']
        voucher.usage = form.cleaned_data['usage']
        voucher.start_datetime = form.cleaned_data['start_datetime']
        voucher.end_datetime = form.cleaned_data['end_datetime']
        voucher.min_odr_amount = form.cleaned_data['min_odr_amount']
        voucher.shipping_method = form.cleaned_data['shipping_method']
        voucher.save()

        offer = voucher.offers.all()[0]
        offer.condition.range = form.cleaned_data['benefit_range']
        offer.condition.range_destination = form.cleaned_data['destination_range']
        offer.condition.save()

        offer.exclusive = form.cleaned_data['exclusive']
        offer.save()

        benefit = voucher.benefit
        benefit.range = form.cleaned_data['benefit_range']
        benefit.type = form.cleaned_data['benefit_type']
        benefit.value = form.cleaned_data['benefit_value']
        benefit.save()

        return HttpResponseRedirect(self.get_success_url())


class VoucherDeleteView(VoucherDeleteViewCustom):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        offers = self.object.offers.get()
        success_url = self.get_success_url()
        offers.delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)
