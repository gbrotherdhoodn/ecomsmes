from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class
from .views import product_review_list, add_delete_product_to_wishlist


class BaseCatalogueApplication(Application):
    name = 'catalogue'
    detail_view = get_class('catalogue.views', 'ProductDetailView')
    catalogue_view = get_class('catalogue.views', 'CatalogueView')
    category_view = get_class('catalogue.views', 'ProductCategoryView')
    range_view = get_class('offer.views', 'RangeDetailView')
    wishlist_view = add_delete_product_to_wishlist
    review_list_view = product_review_list

    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^$', self.catalogue_view.as_view(), name='index'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            # Fallback URL if a user chops of the last part of the URL
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/$',
                self.category_view.as_view()),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/wish-list/',
                self.wishlist_view, name='ajax-add-delete-wish-list'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/review-list/',
                self.review_list_view, name='ajax-review-list')
        ]
        return self.post_process_urls(urlpatterns)


class ReviewsApplication(Application):
    name = None
    reviews_app = get_class('catalogue.reviews.app', 'application')

    def get_urls(self):
        urlpatterns = super(ReviewsApplication, self).get_urls()
        urlpatterns += [
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/',
                self.reviews_app.urls)
        ]
        return self.post_process_urls(urlpatterns)


class CatalogueApplication(BaseCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()
