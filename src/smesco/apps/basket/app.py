from django.conf.urls import url
from oscar.core.application import Application
from oscar.core.loading import get_class


class BasketApplication(Application):
    name = 'basket'
    summary_view = get_class('basket.views', 'BasketView')
    add_view = get_class('basket.views', 'BasketAddView')
    add_voucher_view = get_class('basket.views', 'VoucherAddView')
    remove_voucher_view = get_class('basket.views', 'VoucherRemoveView')

    def get_urls(self):
        urls = [
            url(r'^$', self.summary_view.as_view(), name='summary'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$', self.remove_voucher_view.as_view(),
                name='vouchers-remove'),

        ]

        return self.post_process_urls(urls)


application = BasketApplication()
