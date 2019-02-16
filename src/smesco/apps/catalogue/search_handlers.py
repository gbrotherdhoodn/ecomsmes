from oscar.apps.catalogue.search_handlers import SolrProductSearchHandler as SolrProductSearchHandlerCustom


class SolrProductSearchHandler(SolrProductSearchHandlerCustom):

    def get_search_queryset(self):
        sqs = super(SolrProductSearchHandler, self).get_search_queryset()
        sqs = sqs.narrow('structure_exact:("child" OR "standalone")')
        if self.categories:
            pattern = ' OR '.join([
                '"%s"' % sqs.query.clean(c.full_name) for c in self.categories])
            sqs = sqs.narrow('category_exact:(%s)' % pattern)

        return sqs
