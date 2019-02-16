from oscar.apps.basket.abstract_models import AbstractLine, AbstractBasket


class Basket(AbstractBasket):

    @property
    def total_excl_tax_without_voucher(self):
        """
        Return total line price excluding tax
        """
        return self._get_total('line_price_excl_tax_incl_discounts_without_voucher')

    @property
    def total_incl_tax_without_voucher(self):
        """
        Return total price inclusive of tax and discounts
        """
        return self._get_total('line_price_incl_tax_incl_discounts_without_voucher')


class Line(AbstractLine):

    @property
    def unit_price_excl_tax_incl_discount(self):
        if self.has_discount:
            return self.purchase_info.price.excl_tax_incl_discount
        else:
            return self.unit_price_excl_tax

    @property
    def unit_price_incl_tax_incl_discount(self):
        if self.has_discount:
            return self.purchase_info.price.incl_tax_incl_discount
        else:
            return self.unit_price_incl_tax

    @property
    def line_price_excl_tax_incl_discounts_without_voucher(self):
        if self.unit_price_excl_tax_incl_discount is not None:
            return self.quantity * self.unit_price_excl_tax_incl_discount

    @property
    def line_price_incl_tax_incl_discounts_without_voucher(self):
        if self.unit_price_incl_tax_incl_discount is not None:
            return self.quantity * self.unit_price_incl_tax_incl_discount

from oscar.apps.basket.models import *  # noqa isort:skip
