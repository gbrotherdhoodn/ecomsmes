from oscar.apps.order.processing import EventHandler as OriginalEventHandler
from apps.partner_api.tasks import send_email_order
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from oscar.core.loading import get_model

from apps.order.models import STATUS_SHIPPED, STATUS_CANCELED

OrderNote = get_model('order', 'OrderNote')


class EventHandler(OriginalEventHandler):

    def handle_order_status_change(self, order, new_status, note_msg=None):
        """
        Handle a requested order status change

        This method is not normally called directly by client code.  The main
        use-case is when an order is cancelled, which in some ways could be
        viewed as a shipping event affecting all lines.
        """

        old_status = order.status
        new_status = new_status
        order.set_status(new_status)
        msg = _("Order status changed from '%(old_status)s' to"
                " '%(new_status)s'") % {'old_status': old_status,
                                        'new_status': new_status}
        if note_msg:
            msg = note_msg

        for line in order.lines.all():
            line.set_status(new_status)

        if new_status in getattr(settings, 'REPLACEMENT_STOCK_STATUS'):
            self.update_stock_records(old_status, new_status, order.basket.all_lines())

        self.create_note(order, msg, old_status)
        send_email_order.delay(new_status, order.id)

    def create_note(self, order, message, old_status, note_type=OrderNote.SYSTEM):
        return order.notes.create(
            message=message, note_type=note_type, user=self.user,
            old_status=old_status, new_status=order.status)

    def update_stock_records(self, old_status, new_status, lines):
        if new_status == STATUS_SHIPPED:
            for line in lines:
                line.stockrecord.consume_allocation(line.quantity)
        elif new_status == STATUS_CANCELED:
            if old_status == STATUS_SHIPPED:
                for line in lines:
                    line.stockrecord.cancel_allocation_shipping(line.quantity)
            else:
                for line in lines:
                    line.stockrecord.cancel_allocation(line.quantity)
