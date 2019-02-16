from decimal import Decimal as D

from oscar.core import prices

from apps.catalogue.models import Product, ProductAttribute, ProductAttributeValue
from apps.partner_api.client import get_kgx_client


def calculate_kgx(result, basket, postcode):
    basket_products = basket._lines
    weight = 0
    for basket_product in basket_products:
        product = Product.objects.get(id=basket_product.product_id)
        product = Product.objects.get(id=product.parent_id) if product.parent_id else product

        try:
            attribute_id = ProductAttribute.objects.get(product_class_id=product.product_class_id, code='berat')
        except ProductAttribute.DoesNotExist:
            result['error'] = "Tidak Tersedia"
            return result

        try:
            product_attribute = ProductAttributeValue.objects.get(product_id=basket_product.product_id,
                                                                  attribute_id=attribute_id)
            if product_attribute.value:
                weight += product_attribute.value * basket_product.quantity
            else:
                result['error'] = "Tidak Tersedia"
                return result
        except ProductAttributeValue.DoesNotExist:
            result['error'] = "Tidak Tersedia"
            return result

    return result_kgx(weight, result, basket.currency, postcode)


def result_kgx(weight, result, basket_currency, postcode):
    kgx_client = get_kgx_client()
    kgx_rate = kgx_client.check_rate(postcode, weight)
    if kgx_rate and kgx_rate['status'] == 200:
        kgx_data = kgx_rate['data']['services']['reg']
        final_cost = kgx_data['FinalCost']
        min_day = kgx_data['MinLeadTime']
        max_day = kgx_data['MaxLeadTime']

        result['price'] = prices.Price(currency=basket_currency, excl_tax=D(final_cost), incl_tax=D(final_cost))
        result['estimate'] = '%s - %s Hari' % (min_day, max_day,)
        return result
    else:
        result['error'] = "Tidak Tersedia"
        return result
