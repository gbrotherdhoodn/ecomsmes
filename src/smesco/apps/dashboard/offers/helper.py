

# Helper for updating price index in solr
def update_product_offer_range_price(range):

    for range_category in range.included_categories.all():
        for product_category in range_category.productcategory_set.all():
            product_category.product.save()

    for product in range.included_products.all():
        product.save()

    for product_excluded in range.excluded_products.all():
        product_excluded.save()
