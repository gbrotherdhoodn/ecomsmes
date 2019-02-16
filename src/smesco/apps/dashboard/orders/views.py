from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.orders.views import OrderDetailView as OrderDetailViewCustom, \
    OrderListView as OrderListViewCustom
from apps.dashboard.orders.helpers import get_history_shipping
from .services import order_change_status_services


class OrderListView(OrderListViewCustom):
    _shipping_events = None

    def change_order_status(self, request, order):
        new_status = request.POST['new_status'].strip()
        if not new_status:
            messages.error(request, _("The new status '%s' is not valid")
                           % new_status)
        elif new_status not in order.available_statuses():
            messages.error(request, _("The new status '%s' is not valid for"
                                      " this order") % new_status)
        else:
            order_change_status_services(order, new_status, request, self._shipping_events)


class OrderDetailView(OrderDetailViewCustom):
    _shipping_events = None

    def get_context_data(self, **kwargs):
        ctx = super(OrderDetailView, self).get_context_data(**kwargs)
        ctx['shipping_events_new'] = get_history_shipping(ctx['order'])

        return ctx

    def change_order_status(self, request, order):
        form = self.get_order_status_form()
        if not form.is_valid():
            return self.reload_page(error=_("Invalid form submission"))

        new_status = form.cleaned_data['new_status']
        order_change_status_services(order, new_status, request, self._shipping_events)
        return self.reload_page()

