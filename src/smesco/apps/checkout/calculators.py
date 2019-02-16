from oscar.core import prices


class OrderTotalCalculator(object):

    def __init__(self, request=None):
        self.request = request

    def calculate(self, basket, shipping_charge, **kwargs):
        if isinstance(shipping_charge, str):
            return prices.Price(currency=basket.currency, excl_tax=None, incl_tax=None)

        if isinstance(shipping_charge, dict):
            if isinstance(shipping_charge['price'], str):
                return prices.Price(currency=basket.currency, excl_tax=None, incl_tax=None)

            excl_tax = basket.total_excl_tax + shipping_charge['price'].excl_tax
            if basket.is_tax_known and shipping_charge['price'].is_tax_known:
                incl_tax = basket.total_incl_tax + shipping_charge['price'].incl_tax
            else:
                incl_tax = None
        else:
            excl_tax = basket.total_excl_tax + shipping_charge.excl_tax
            if basket.is_tax_known and shipping_charge.is_tax_known:
                incl_tax = basket.total_incl_tax + shipping_charge.incl_tax
            else:
                incl_tax = None
        return prices.Price(
            currency=basket.currency,
            excl_tax=excl_tax, incl_tax=incl_tax)
