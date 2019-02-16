from oscar.apps.offer.applicator import Applicator  # backwards-compat  # noqa


def unit_price(offer, line):
    """
    Return the relevant price for a given basket line.

    This is required so offers can apply in circumstances where tax isn't known
    """
    if offer.offer_type == offer.VOUCHER:
        return line.unit_price_excl_tax_incl_discount
    else:
        return line.unit_effective_price
