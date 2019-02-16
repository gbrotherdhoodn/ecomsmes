from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from oscar.apps.order import exceptions as order_exceptions
from oscar.apps.payment.exceptions import PaymentError
from apps.partner_api.client import get_kgx_client
from apps.order.models import STATUS_SHIPPED
from apps.dashboard.orders.helpers import add_shipping_event, get_total_weight
from oscar.core.loading import get_class, get_model


EventHandler = get_class('order.processing', 'EventHandler')
OrderNote = get_model('order', 'OrderNote')


def order_change_status_services(order, new_status, request, shipping_events):
    old_status, new_status = order.status, new_status

    try:
        # if new_status in [STATUS_CANCELED, STATUS_COMPLETED]:
            # cancel_payment = process_cancel_order(request, order.number)
            # if cancel_payment['status_code'] != OK:
            #     messages.error(
            #         request, _("Cannot change order status because cancel payment was unsuccessful"))
            #     return redirect('dashboard:order-list')
        if new_status == STATUS_SHIPPED:
            if order.shipping_code == 'kgx-courier':
                kgx_client = get_kgx_client()
                create_shipping_order = kgx_client.create_order(order, get_total_weight(order.basket.all_lines()))
                if create_shipping_order and create_shipping_order['status'] == 200:
                    add_shipping_event(shipping_events, STATUS_SHIPPED, order,
                                       create_shipping_order['data']['order_number'])
                else:
                    messages.error(
                        request, "Unable to change order status due to KGX API error: %s - %s" % (
                            create_shipping_order['status'], create_shipping_order['message']))

        handler = EventHandler(request.user)
        handler.handle_order_status_change(order, new_status)

    except PaymentError as e:
        messages.error(
            request, _("Unable to change order status due to "
                       "payment error: %s") % e)
    except order_exceptions.InvalidOrderStatus as e:
        messages.error(
            request, _("Unable to change order status as the requested "
                       "new status is not valid"))
    else:
        msg = _("Order '%(number)s' status changed from '%(old_status)s' to"
                " '%(new_status)s'") % {'number': order.number,
                                        'old_status': old_status,
                                        'new_status': new_status}
        messages.info(request, msg)


