import logging
from django import http
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from oscar.core.loading import get_model
from apps.checkout.views import PaymentDetailsView as OriginalPaymentDetailsView
from django.views.decorators.csrf import csrf_exempt
from .forms import PaymentNotificationsForm
from .utils import PaymentServices

log = logging.getLogger('smesco')
Order = get_model('order', 'Order')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')


class PaymentDetailsView(OriginalPaymentDetailsView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_method'] = self.request.POST.get("payment-method", "")
        return context

    def handle_payment(self, order_number, total, **kwargs):
        log.info(f"start handle payment for order {order_number}")
        ctx = self.get_context_data()
        payment_method = ctx.get('payment_method', None)
        if not payment_method:
            log.warning(f"payment method None for Order {order_number}")
            return http.HttpResponseBadRequest()

        source_type = SourceType.objects.filter(code=payment_method).last()

        if not source_type:
            log.warning(f"payment method code {payment_method} was illegal for Order {order_number}")
            return http.HttpResponseBadRequest()

        source = Source(
            source_type=source_type,
            amount_allocated=total.incl_tax)
        self.add_payment_source(source)


@csrf_exempt
def payment_response(request, order_number):
    next_url = request.GET.get('next', None)
    if request.method == 'POST':
        data = request.POST
        order = get_object_or_404(Order, number=order_number)
        form = PaymentNotificationsForm(data)

        if not form.is_valid():
            log.error(form.errors)
            return http.HttpResponseBadRequest()

        cleaned_data = form.cleaned_data
        payment_services = PaymentServices()
        log.info('Masuk Pengecekan Status %s' % cleaned_data)
        success, msg = payment_services.payment_receive_services(order, **cleaned_data)
        log.info(f'Message for payment order {order.number}: {msg}')

        if success:
            messages.success(request, msg)
            return render(request, 'checkout/thank_you.html', {'order': order})
        else:
            messages.add_message(request, messages.ERROR, msg)
            return http.HttpResponseRedirect(next_url)
    else:
        return http.HttpResponseForbidden()


@csrf_exempt
def payment_notifications(request, order_number):
    if request.method == 'POST':
        data = request.POST
        order = get_object_or_404(Order, number=order_number)
        form = PaymentNotificationsForm(data)

        if not form.is_valid():
            log.error(form.errors)
            return http.HttpResponseBadRequest()

        cleaned_data = form.cleaned_data
        payment_services = PaymentServices()
        log.info('Masuk Pengecekan Status %s' % cleaned_data)
        success, msg = payment_services.payment_receive_services(order, **cleaned_data)
        log.info(f'Message for payment order {order.number}: {msg}')
        return http.HttpResponse('RECEIVEOK')
    else:
        return http.HttpResponseForbidden()
