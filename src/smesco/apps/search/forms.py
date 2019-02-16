from collections import defaultdict

from django.conf import settings
from haystack.forms import FacetedSearchForm

from oscar.core.loading import get_class
from oscar.apps.search.forms import SearchForm as SearchFormCustom

is_solr_supported = get_class('search.features', 'is_solr_supported')

VALID_FACET_QUERIES = defaultdict(list)
for facet in settings.OSCAR_SEARCH_FACETS['queries'].values():
    field_name = "%s_exact" % facet['field']
    queries = [t[1] for t in facet['queries']]
    VALID_FACET_QUERIES[field_name].extend(queries)


class SearchForm(SearchFormCustom):

    def search(self):

        sqs = super(FacetedSearchForm, self).search()

        for field, values in self.selected_multi_facets.items():
            if not values:
                continue
            if field in VALID_FACET_QUERIES:
                sqs = sqs.narrow(u'%s:(%s)' % (
                    field, " OR ".join(values)))
            else:
                clean_values = [
                    '"%s"' % sqs.query.clean(val) for val in values]
                sqs = sqs.narrow(u'%s:(%s)' % (
                    field, " OR ".join(clean_values)))

        if self.is_valid() and 'sort_by' in self.cleaned_data:
            sort_field = self.SORT_BY_MAP.get(
                self.cleaned_data['sort_by'], None)
            if sort_field:
                sqs = sqs.order_by(sort_field)

        sqs = sqs.narrow('structure_exact:("child" OR "standalone")')

        return sqs

    @property
    def selected_multi_facets(self):
        selected_multi_facets = defaultdict(list)

        for facet_kv in self.selected_facets:
            if ":" not in facet_kv:
                continue
            field_name, value = facet_kv.split(':', 1)

            # EDITED PART comparing to original Oscar source
            # Validate query facets as they as passed unescaped to Solr
            if field_name in VALID_FACET_QUERIES:
                if field_name in settings.OSCAR_SEARCH_FACETS['dynamic_queries_field_names']:
                    pass
                else:
                    if value not in VALID_FACET_QUERIES[field_name]:
                        # Invalid query value
                        continue
            # END

            selected_multi_facets[field_name].append(value)

        return selected_multi_facets


class BrowseCategoryForm(SearchForm):

    def no_query_found(self):
        return self.searchqueryset
