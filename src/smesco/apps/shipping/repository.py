from decimal import Decimal as D

from . import methods as shipping_method

from oscar.apps.shipping import repository
from oscar.core.loading import get_classes

(Free, NoShippingRequired,
 TaxExclusiveOfferDiscount, TaxInclusiveOfferDiscount) \
    = get_classes('shipping.methods', ['Free', 'NoShippingRequired',
                                       'TaxExclusiveOfferDiscount', 'TaxInclusiveOfferDiscount'])


class Repository(repository.Repository):

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
        methods = [shipping_method.Kgx(shipping_address=shipping_addr)]

        return methods

    def apply_shipping_offer(self, basket, method, offer):

        charge = method.calculate(basket)

        if isinstance(charge, dict):
            charge = charge.get('price')

        if isinstance(charge, str):
            return method

        if charge.excl_tax == D('0.00'):
            return method

        if charge.is_tax_known:
            return TaxInclusiveOfferDiscount(method, offer)
        else:
            return TaxExclusiveOfferDiscount(method, offer)
