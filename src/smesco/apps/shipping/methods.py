from decimal import Decimal as D

from oscar.apps.shipping import methods
from oscar.core import prices
from .helpers import calculate_kgx


class Kgx(methods.Base):
    code = 'kgx-courier'
    name = 'KGX Kurir'
    description = 'Kurir KGX'

    def __init__(self, shipping_address):
        self.shipping_address = shipping_address

    def calculate(self, basket):
        result = {
            'price': '',
            'estimate': '',
            'error': ''
        }
        if self.shipping_address:
            return calculate_kgx(result, basket, self.shipping_address.postcode)
        else:
            result['price'] = prices.Price(currency=basket.currency, excl_tax=D('0.00'), incl_tax=D('0.00'))
            return result


class TaxExclusiveOfferDiscount(methods.TaxExclusiveOfferDiscount):

    def calculate(self, basket):
        result = {
            'price': '',
            'estimate': '',
            'error': ''
        }

        result_method = calculate_kgx(result, basket, self.method.shipping_address.postcode)
        base_charge = self.method.calculate(basket)

        if isinstance(base_charge, dict):
            base_charge = base_charge.get('price')

        discount = self.offer.shipping_discount(base_charge.excl_tax)
        excl_tax = base_charge.excl_tax - discount
        result_method['price'] = prices.Price(currency=base_charge.currency, excl_tax=excl_tax)
        return result_method

    def discount(self, basket):
        base_charge = self.method.calculate(basket)

        if isinstance(base_charge, dict):
            base_charge = base_charge.get('price')

        return self.offer.shipping_discount(base_charge.excl_tax)


class TaxInclusiveOfferDiscount(methods.TaxInclusiveOfferDiscount):

    def calculate(self, basket):
        result = {
            'price': '',
            'estimate': '',
            'error': ''
        }

        result_method = calculate_kgx(result, basket, self.method.shipping_address.postcode)
        base_charge = self.method.calculate(basket)

        if isinstance(base_charge, dict):
            base_charge = base_charge.get('price')

        discount = self.offer.shipping_discount(base_charge.incl_tax)
        incl_tax = base_charge.incl_tax - discount
        excl_tax = self.calculate_excl_tax(base_charge, incl_tax)
        result_method['price'] = prices.Price(currency=base_charge.currency, excl_tax=excl_tax, incl_tax=incl_tax)
        return result_method

    def calculate_excl_tax(self, base_charge, incl_tax):

        if incl_tax == D('0.00'):
            return D('0.00')

        excl_tax = base_charge.excl_tax * (
            incl_tax / base_charge.incl_tax)
        return excl_tax.quantize(D('0.01'))

    def discount(self, basket):
        base_charge = self.method.calculate(basket)

        if isinstance(base_charge, dict):
            base_charge = base_charge.get('price')

        return self.offer.shipping_discount(base_charge.incl_tax)
