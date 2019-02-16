import json

from django.conf import settings
from haystack.query import SearchQuerySet
from oscar.core.loading import get_class, get_model

from oscar.apps.search.views import FacetedSearchView as FacetedSearchViewCustom

FacetMunger = get_class('search.facets', 'FacetMunger')
Product = get_model('catalogue', 'Product')


class FacetedSearchView(FacetedSearchViewCustom):

    def extra_context(self):
        extra = super(FacetedSearchView, self).extra_context()

        if self.results.query.backend.include_spelling:
            suggestion = self.form.get_suggestion()
            if suggestion != self.query:
                extra['suggestion'] = suggestion

        if 'fields' in extra['facets']:
            munger = FacetMunger(
                self.request.get_full_path(),
                self.form.selected_multi_facets,
                self.results.facet_counts())
            extra['facet_data'] = munger.facet_data()
            has_facets = any([len(data['results']) for
                              data in extra['facet_data'].values()])
            extra['has_facets'] = has_facets

        extra['selected_facets'] = self.request.GET.getlist('selected_facets')

        price_stats = SearchQuerySet().models(Product).stats('price').stats_results()['price']
        min_category_price, max_category_price = round(price_stats['min']), round(price_stats['max'])

        dynamic_query_fields = json.dumps(settings.OSCAR_SEARCH_FACETS['dynamic_queries_field_names'])

        extra['facet_data']['price_range']['results'] = dict(min_category_price=min_category_price,
                                                             max_category_price=max_category_price,
                                                             dynamic_query_fields=dynamic_query_fields)

        return extra
