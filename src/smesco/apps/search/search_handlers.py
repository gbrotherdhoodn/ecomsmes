from django.conf import settings
from haystack.query import SearchQuerySet
from oscar.apps.search.search_handlers import *


class SearchHandler(SearchHandler):

    def get_search_results(self, search_form):
        return search_form.search()

    def get_search_context_data(self, context_object_name=None):

        munger = self.get_facet_munger()
        facet_data = munger.facet_data()
        has_facets = any([data['results'] for data in facet_data.values()])

        # ADDED PART FOR PRICE INPUT FIELD
        from apps.catalogue.models import Product

        price_stats = SearchQuerySet().models(Product).stats('price').stats_results()['price']
        if price_stats:
            min_category_price, max_category_price = round(price_stats.get('min') or 0), \
                                                     round(price_stats.get('max') or 999999)

            dynamic_query_fields = settings.OSCAR_SEARCH_FACETS['dynamic_queries_field_names']

            facet_data['price_range']['results'] = dict(min_category_price=min_category_price,
                                                        max_category_price=max_category_price,
                                                        dynamic_query_fields=dynamic_query_fields)
        # END

        context = {
            'facet_data': facet_data,
            'has_facets': has_facets,
            'selected_facets': self.request_data.getlist('selected_facets'),
            'form': self.search_form,
            'paginator': self.paginator,
            'page_obj': self.page,
        }

        if context_object_name is not None:
            context[context_object_name] = self.get_paginated_objects()

        return context
