from oscar.apps.checkout.mixins import OrderPlacementMixin as OriginalOrderPlacementMixin
from apps.partner_api.tasks import send_email_order
from oscar.core.loading import get_class, get_model
from django.conf import settings

OrderCreator = get_class('order.utils', 'OrderCreator')
OrderNote = get_model('order', 'OrderNote')


class OrderPlacementMixin(OriginalOrderPlacementMixin):

    def place_order(self, order_number, user, basket, shipping_address,
                    shipping_method, shipping_charge, order_total,
                    billing_address=None, **kwargs):
        """
        Writes the order out to the DB including the payment models
        """

        # Create saved shipping address instance from passed in unsaved
        # instance
        shipping_address = self.create_shipping_address(user, shipping_address)

        # We pass the kwargs as they often include the billing address form
        # which will be needed to save a billing address.
        billing_address = self.create_billing_address(
            user, billing_address, shipping_address, **kwargs)

        if 'status' not in kwargs:
            status = getattr(settings, 'ORDER_STATUS_PLACED')
        else:
            status = kwargs.pop('status')

        if 'request' not in kwargs:
            request = getattr(self, 'request', None)
        else:
            request = kwargs.pop('request')

        order = OrderCreator().place_order(
            user=user,
            order_number=order_number,
            basket=basket,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            shipping_charge=shipping_charge,
            total=order_total,
            billing_address=billing_address,
            status=status,
            request=request,
            **kwargs)
        self.save_payment_details(order)
        self.create_note(order, 'Order Placed', '', user)
        send_email_order.delay(status, order.id)
        return order

    def create_note(self, order, message, old_status, user, note_type=OrderNote.SYSTEM):
        return order.notes.create(
            message=message, note_type=note_type, user=user,
            old_status=old_status, new_status=order.status)
