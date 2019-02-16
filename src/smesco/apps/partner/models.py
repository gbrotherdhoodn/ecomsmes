from oscar.apps.partner.abstract_models import AbstractStockRecord
from decimal import Decimal
from apps.offer.models import Benefit

class StockRecord(AbstractStockRecord):

    def cancel_allocation_shipping(self, quantity):
        if not self.can_track_allocations:
            return

        self.num_in_stock += quantity
        self.save()
    cancel_allocation_shipping.alters_data = True

    # =======
    # Helpers
    # =======

    def get_discount_price(self, offer):


        price = Decimal(self.price_excl_tax)
        total = price
        offer_type = offer.benefit.type
        discount = offer.benefit.value
        if offer_type == Benefit.FIXED:
            if discount > price:
                total = 0
            else:
                total = price - discount
        elif offer_type == Benefit.PERCENTAGE:
            total = price - ((price * discount) / 100)
        elif offer_type == Benefit.FIXED_PRICE:
            total = discount

        return total

    # ==========
    # Properties
    # ==========

    @property
    def price_excl_tax_incl_discount(self):
        if self.product.offer_discounts.get('is_available'):
            price = self.get_discount_price(self.product.offer_discounts.get('discount'))
        else:
            price = self.price_excl_tax
        return price


from oscar.apps.partner.models import *  # noqa isort:skip
