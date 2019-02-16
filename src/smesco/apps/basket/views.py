from django import shortcuts
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer
from oscar.apps.basket.views import BasketView as BasketCustomView
from oscar.apps.basket.views import BasketAddView as BasketCustomAddView
from oscar.apps.basket.views import VoucherAddView as VoucherCustomAddView
from oscar.apps.basket.views import VoucherRemoveView as VoucherCustomRemoveView
from oscar.apps.basket.signals import voucher_addition, basket_addition, voucher_removal
from apps.checkout.calculators import OrderTotalCalculator
from apps.offer.models import STATE, DISTRICT, SUBDISTRICT, ALLAREA, VILLAGE


Applicator = get_class('offer.applicator', 'Applicator')
(BasketLineForm, AddToBasketForm, BasketVoucherForm, SavedLineForm) = get_classes(
    'basket.forms', ('BasketLineForm', 'AddToBasketForm',
                     'BasketVoucherForm', 'SavedLineForm'))
BasketLineFormSet, SavedLineFormSet = get_classes('basket.formsets', ('BasketLineFormSet', 'SavedLineFormSet'))
BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')


class BasketView(BasketCustomView):

    def is_voucher_available(self):

        available = False
        for voucher in self.request.basket.grouped_voucher_discounts:
            self.request.basket.vouchers.remove(voucher.get('voucher'))
            voucher_removal.send(sender=self, basket=self.request.basket, voucher=voucher.get('voucher'))
            available = True

        for voucher in self.request.basket.shipping_discounts:
            self.request.basket.vouchers.remove(voucher.get('voucher'))
            voucher_removal.send(sender=self, basket=self.request.basket, voucher=voucher.get('voucher'))
            available = True

        return available

    def get(self, request, *args, **kwargs):
        if self.is_voucher_available():
            return redirect('basket:summary')
        return super(BasketView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BasketView, self).get_context_data(**kwargs)
        context['voucher_form'] = self.get_basket_voucher_form()

        context['shipping_methods'] = self.get_shipping_methods(
            self.request.basket)
        method = self.get_default_shipping_method(self.request.basket)
        context['shipping_method'] = method
        shipping_charge = method.calculate(self.request.basket)
        context['shipping_charge'] = shipping_charge
        if method.is_discounted:
            excl_discount = method.calculate_excl_discount(self.request.basket)
            context['shipping_charge_excl_discount'] = excl_discount

        context['order_total'] = OrderTotalCalculator().calculate(
            self.request.basket, shipping_charge)
        context['basket_warnings'] = self.get_basket_warnings(
            self.request.basket)
        context['upsell_messages'] = self.get_upsell_messages(
            self.request.basket)

        if self.request.user.is_authenticated:
            try:
                saved_basket = self.basket_model.saved.get(
                    owner=self.request.user)
            except self.basket_model.DoesNotExist:
                pass
            else:
                saved_basket.strategy = self.request.basket.strategy
                if not saved_basket.is_empty:
                    saved_queryset = saved_basket.all_lines()
                    formset = SavedLineFormSet(strategy=self.request.strategy,
                                               basket=self.request.basket,
                                               queryset=saved_queryset,
                                               prefix='saved')
                    context['saved_formset'] = formset
        return context


class BasketAddView(BasketCustomAddView):
    form_class = AddToBasketForm
    product_model = get_model('catalogue', 'product')
    add_signal = basket_addition
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.product = shortcuts.get_object_or_404(
            self.product_model, pk=kwargs['pk'])
        return super(BasketAddView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BasketAddView, self).get_form_kwargs()
        kwargs['basket'] = self.request.basket
        kwargs['product'] = self.product
        return kwargs

    def form_invalid(self, form):
        msgs = []
        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]
        messages.error(self.request, ",".join(clean_msgs))

        return redirect_to_referrer(self.request, 'basket:summary')

    def form_valid(self, form):
        offers_before = self.request.basket.applied_offers()

        messages.success(self.request, self.get_success_message(form),
                         extra_tags='safe noicon')

        BasketMessageGenerator().apply_messages(self.request, offers_before)

        return super(BasketAddView, self).form_valid(form)


class VoucherAddView(VoucherCustomAddView):
    voucher_model = get_model('voucher', 'voucher')
    add_signal = voucher_addition

    def apply_voucher_to_basket(self, voucher):
        if voucher.is_expired():
            messages.error(
                self.request,
                _("Voucher '%(code)s' telah kedaluwarsa") % {
                    'code': voucher.code})
            return

        if not voucher.is_active():
            messages.error(
                self.request,
                _("Voucher '%(kode)s' tidak aktif") % {
                    'code': voucher.code})
            return

        is_available, message = voucher.is_available_to_user(self.request.user)
        if not is_available:
            messages.error(self.request, message)
            return

        if self.request.POST['method'] != voucher.shipping_method:
            messages.error(self.request, "Voucher Shipping tidak berlaku")
            return

        if self.request.basket.total_incl_tax < voucher.min_odr_amount:
            messages.error(
                self.request,
                _("Minimal pesanan harus mencapai %(amount)s") % {
                    'amount': voucher.min_odr_amount})
            return

        if not self.is_voucher_available_destination(voucher):
            messages.error(self.request, "Voucher tidak berlaku")
            return

        self.request.basket.vouchers.add(voucher)

        self.add_signal.send(
            sender=self, basket=self.request.basket, voucher=voucher)

        Applicator().apply(self.request.basket, self.request.user,
                           self.request)

        discounts_after = self.request.basket.offer_applications

        found_discount = False
        for discount in discounts_after:
            if discount['voucher'] and discount['voucher'] == voucher:
                found_discount = True
                break
        if not found_discount:
            messages.warning(
                self.request,
                _("Keranjang Anda tidak memenuhi syarat untuk diskon voucher"))
            self.request.basket.vouchers.remove(voucher)
        else:
            messages.info(
                self.request,
                _("Voucher '%(code)s' ditambahkan ke keranjang") % {
                    'code': voucher.code})

    def is_voucher_available_destination(self, voucher):
        destination_range = voucher.offers.all()[0].condition.range_destination

        if destination_range:
            return self.check_destination_range(destination_range, self.request.POST)
        else:
            return True

    @staticmethod
    def check_destination_range(destination_range, posr):
        if destination_range.destination_type == STATE:
            return True if destination_range.destination_id == int(posr.get(STATE)) else False
        elif destination_range.destination_type == DISTRICT:
            return True if destination_range.destination_id == int(posr.get(DISTRICT)) else False
        elif destination_range.destination_type == SUBDISTRICT:
            return True if destination_range.destination_id == int(posr.get(SUBDISTRICT)) else False
        elif destination_range.destination_type == ALLAREA:
            return True
        else:
            return True if destination_range.destination_id == int(posr.get(VILLAGE)) else False


class VoucherRemoveView(VoucherCustomRemoveView):
    voucher_model = get_model('voucher', 'voucher')
    remove_signal = voucher_removal
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        response = redirect('checkout:payment-details')

        voucher_id = kwargs['pk']
        if not request.basket.id:
            return response
        try:
            voucher = request.basket.vouchers.get(id=voucher_id)
        except ObjectDoesNotExist:
            messages.error(
                request, _("Tidak ada voucher dengan id '%s'") % voucher_id)
        else:
            request.basket.vouchers.remove(voucher)
            self.remove_signal.send(
                sender=self, basket=request.basket, voucher=voucher)
            messages.info(
                request, _("Voucher '%s' dihapus dari keranjang") % voucher.code)

        return response
