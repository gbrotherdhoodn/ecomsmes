import logging

from django import http
from django.views import generic
from django.conf import settings
from django.shortcuts import redirect
from django.utils import six
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from oscar.core.loading import get_class, get_classes, get_model
from apps.payment.utils import ipay_signature_creator, get_complete_url

from oscar.apps.checkout import signals
from oscar.apps.checkout.views import PaymentDetailsView as PaymentCustomDetailsView
from oscar.apps.checkout.views import ShippingAddressView as ShippingAddressMethodView
from apps.offer.models import STATE, DISTRICT, SUBDISTRICT, ALLAREA
from apps.templatetags.utils_tags import get_total_before_voucher
from oscar.apps.basket.signals import voucher_removal


from oscar.core.compat import get_user_model


ShippingAddressForm, ShippingMethodForm, GatewayForm \
    = get_classes('checkout.forms', ['ShippingAddressForm', 'ShippingMethodForm', 'GatewayForm'])
OrderCreator = get_class('order.utils', 'OrderCreator')
UserAddressForm = get_class('address.forms', 'UserAddressForm')
Repository = get_class('shipping.repository', 'Repository')
AccountAuthView = get_class('customer.views', 'AccountAuthView')
RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
NoShippingRequired = get_class('shipping.methods', 'NoShippingRequired')


Order = get_model('order', 'Order')
ShippingAddress = get_model('order', 'ShippingAddress')
CommunicationEvent = get_model('order', 'CommunicationEvent')
Product = get_model('catalogue', 'Product')
PaymentEventType = get_model('order', 'PaymentEventType')
PaymentEvent = get_model('order', 'PaymentEvent')
UserAddress = get_model('address', 'UserAddress')
Basket = get_model('basket', 'Basket')
Email = get_model('customer', 'Email')
Country = get_model('address', 'Country')
SourceType = get_model('payment', 'SourceType')
CommunicationEventType = get_model('customer', 'CommunicationEventType')

# Standard logger for checkout events
logger = logging.getLogger('oscar.checkout')

User = get_user_model()


class ShippingAddressView(ShippingAddressMethodView):
    """
        Determine the shipping address for the order.

        The default behaviour is to display a list of addresses from the users's
        address book, from which the user can choose one to be their shipping
        address.  They can add/edit/delete these USER addresses.  This address will
        be automatically converted into a SHIPPING address when the user checks
        out.

        Alternatively, the user can enter a SHIPPING address directly which will be
        saved in the session and later saved as ShippingAddress model when the
        order is successfully submitted.
        """
    template_name = 'checkout/shipping_address.html'
    form_class = UserAddressForm
    payment_url = reverse_lazy('checkout:payment-method')
    success_url = reverse_lazy('checkout:shipping-address')
    pre_conditions = ['check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_user_email_is_captured']
    skip_conditions = ['skip_unless_basket_requires_shipping']

    def is_voucher_available(self, shipping_address):

        available = True
        for voucher in self.request.basket.shipping_discounts:
            destination_range = voucher['voucher'].offers.all()[0].condition.range_destination

            if destination_range:
                available = self.check_destination_range(destination_range, shipping_address)
            else:
                available = True

            if available:
                self.request.basket.vouchers.remove(voucher.get('voucher'))
                voucher_removal.send(sender=self, basket=self.request.basket, voucher=voucher.get('voucher'))

        return available

    @staticmethod
    def check_destination_range(destination_range, shipping_address):
        if destination_range.destination_type == STATE:
            return True if destination_range.destination_id == shipping_address.province_id else False
        elif destination_range.destination_type == DISTRICT:
            return True if destination_range.destination_id == shipping_address.regency_district_id else False
        elif destination_range.destination_type == SUBDISTRICT:
            return True if destination_range.destination_id == shipping_address.subdistrict_id else False
        elif destination_range.destination_type == ALLAREA:
            return True
        else:
            return True if destination_range.destination_id == shipping_address.village_id else False

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                address = UserAddress.objects.get(
                    is_default_for_billing=True, user_id=request.user.id)
                self.checkout_session.ship_to_user_address(address)
            except UserAddress.DoesNotExist:
                return self.render_to_response(self.get_context_data())

        context = self.get_context_data(**kwargs)

        if not self.is_voucher_available(context.get('shipping_address')):
            return redirect('checkout:shipping-address')

        return self.render_to_response(self.get_context_data())

    def get_initial(self):
        initial = self.checkout_session.new_shipping_address_fields()
        if initial:
            initial = initial.copy()
            # Convert the primary key stored in the session into a Country
            # instance
            try:
                initial['country'] = Country.objects.get(
                    iso_3166_1_a2=initial.pop('country_id'))
            except Country.DoesNotExist:
                # Hmm, the previously selected Country no longer exists. We
                # ignore this.
                pass
        return initial

    def get_form_kwargs(self, **kwargs):
        data = super(ShippingAddressView, self).get_form_kwargs(**kwargs)
        data['user'] = self.request.user
        return data

    def get_context_data(self, **kwargs):
        ctx = super(ShippingAddressView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Look up address book data
            ctx['default_address'] = self.get_default_address()
            ctx['addresses'] = [UserAddressForm(user=self.request.user,
                                                instance=address) for address in self.get_available_addresses()]
            ctx['methods'] = self.get_available_shipping_methods()
        return ctx

    def get_available_addresses(self):
        # Include only addresses where the country is flagged as valid for
        # shipping. Also, use ordering to ensure the default address comes
        # first.
        return self.request.user.addresses.filter(
            country__is_shipping_country=True).order_by(
            '-is_default_for_shipping')[:10]

    def get_default_address(self):
        return self.request.user.addresses.filter(is_default_for_shipping=True,
                                                  is_default_for_billing=True).last()

    def get_available_shipping_methods(self):
        """
        Returns all applicable shipping method objects for a given basket.
        """
        # Shipping methods can depend on the user, the contents of the basket
        # and the shipping address (so we pass all these things to the
        # repository).  I haven't come across a scenario that doesn't fit this
        # system.
        return Repository().get_shipping_methods(
            basket=self.request.basket, user=self.request.user,
            shipping_addr=self.get_shipping_address(self.request.basket),
            request=self.request)

    def post(self, request, *args, **kwargs):
        # Check if a shipping address was selected directly (eg no form was
        # filled in)
        data = self.request.POST
        action = data.get('action', None) or data.get('button_action', None)
        default_address = self.get_default_address()
        if self.request.user.is_authenticated and default_address \
           and action == 'ship_to':
                # User has selected a previous address to ship to
                self.checkout_session.ship_to_user_address(default_address)
                self.checkout_session.use_shipping_method(self.request.POST['method_code'])
                return redirect(self.payment_url)
        elif action == 'user_address_form':
            return super(ShippingAddressView, self).post(
                request, *args, **kwargs)
        else:
            return http.HttpResponseBadRequest()

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class PaymentDetailsView(PaymentCustomDetailsView):
    preview = False
    template_name = 'checkout/payment_details.html'

    def is_voucher_available(self):

        available = False
        for voucher in self.request.basket.grouped_voucher_discounts:
            total_before_voucher = get_total_before_voucher(self.request.basket.total_incl_tax,
                                                            self.request.basket.grouped_voucher_discounts)
            if total_before_voucher < voucher.get('voucher').min_odr_amount:
                self.request.basket.vouchers.remove(voucher.get('voucher'))
                voucher_removal.send(sender=self, basket=self.request.basket, voucher=voucher.get('voucher'))
                available = True

        return available

    def get(self, request, *args, **kwargs):

        if self.is_voucher_available():
            return redirect('checkout:payment-details')

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        if self.is_voucher_available():
            return redirect('checkout:payment-details')

        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)

    def submit(self, user, basket, shipping_address, shipping_method,
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):

        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        # Taxes must be known at this point
        assert basket.is_tax_known, (
            "Basket tax must be set before a user can place an order")
        assert shipping_charge['price'].is_tax_known, (
            "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (eg where we redirect to a 3rd party site and place
        # the order on a different request).
        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d",
                    order_number, basket.id)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing payment on a 3rd party site.  Also, store a reference to
        # the basket in the session so that we know which basket to thaw if we
        # get an unsuccessful payment response when redirecting to a 3rd party
        # site.
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        error_msg = _("A problem occurred while processing payment for this "
                      "order - no payment has been taken.  Please "
                      "contact customer services if this problem persists")

        signals.pre_payment.send_robust(sender=self, view=self)

        try:
            self.handle_payment(order_number, order_total, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e)
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (eg expired bankcard).
            return self.render_payment_details(
                self.request, error=msg, **payment_kwargs)
        except PaymentError as e:
            # A general payment error - Something went wrong which wasn't
            # anticipated.  Eg, the payment gateway is down (it happens), your
            # credentials are wrong - that king of thing.
            # It makes sense to configure the checkout logger to
            # mail admins on an error as this issue warrants some further
            # investigation.
            msg = six.text_type(e)
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge['price'], billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = six.text_type(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

    def handle_successful_order(self, order):
        """
                Handle the various steps required after an order has been successfully
                placed.

                Override this view if you want to perform custom actions when an
                order is submitted.
                """

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id

        response = HttpResponseRedirect(self.get_success_url(order.number))
        self.send_signal(self.request, response, order)
        return response

    def get_success_url(self, order_number=None):
        if order_number:
            return reverse_lazy('checkout:order-summary',  args=(),
                                kwargs={'order_number': order_number})
        return reverse_lazy('checkout:thank-you')


class OrderDetailView(generic.DetailView):
    model = Order

    def get_template_names(self):
        return ["checkout/order_details.html"]

    def get_page_title(self):
        """
        Order number as page title
        """
        return u'%s #%s' % (_('Order'), self.object.number)

    def get_context_data(self, **kwargs):
        ctx = super(OrderDetailView, self).get_context_data(**kwargs)
        order = self.get_object()
        ctx['payment_url'] = getattr(settings, 'IPAY_PAYMENT_URL', None)
        ctx['merchant_code'] = getattr(settings, 'IPAY_MERCHANT_CODE', None)
        ctx['response_url'] = get_complete_url(self.request, 'payment-response', order.number,
                                               'checkout:order-summary')
        ctx['backend_url'] = get_complete_url(self.request, 'payment-notification', order.number)
        ctx['signature_key'] = ipay_signature_creator(order.number, order.total_incl_tax)
        ctx['place_status'] = getattr(settings, 'ORDER_STATUS_PLACED', None)
        return ctx

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, user=self.request.user,
                                 number=self.kwargs['order_number'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != getattr(settings, 'ORDER_STATUS_PLACED', None):
            return http.HttpResponseRedirect(reverse_lazy("customer:order", args=(),
                                             kwargs={'order_number': self.object.number}))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ThankYouOrder(generic.DetailView):

    template_name = 'checkout/thank_you.html'
    context_object_name = 'order'

    def get_object(self):
        # We allow superusers to force an order thank-you page for testing
        order = None
        if self.request.user.is_superuser:
            if 'order_number' in self.kwargs:
                order = Order._default_manager.get(
                    number=self.kwargs['order_number'])
            elif 'order_id' in self.request.GET:
                order = Order._default_manager.get(
                    id=self.request.GET['order_id'])

        if not order:
            if 'checkout_order_id' in self.request.session:
                order = Order._default_manager.get(
                    pk=self.request.session['checkout_order_id'])
            else:
                raise http.Http404(_("No order found"))

        return order
