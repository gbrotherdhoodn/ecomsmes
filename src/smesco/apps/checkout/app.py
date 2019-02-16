from django.contrib.auth.decorators import login_required
from oscar.apps.checkout.app import CheckoutApplication

from apps.payment.views import PaymentDetailsView
from apps.checkout.views import OrderDetailView, ThankYouOrder
from django.conf.urls import url


class OverriddenCheckoutApplication(CheckoutApplication):
    # Specify new view for payment details
    payment_details_view = PaymentDetailsView
    order_details_view = OrderDetailView
    thank_you_order = ThankYouOrder

    def get_urls(self):
        urlpatterns = super(OverriddenCheckoutApplication, self).get_urls()
        urlpatterns += [
            url(r'^order-summary/(?P<order_number>[\w-]*)/$',
                login_required(self.order_details_view.as_view()),
                name='order-summary'),
            url(r'^thank-you/(?P<order_number>[\w-]*)/$',
                login_required(self.thank_you_order.as_view()),
                name='thank-you-order')
        ]
        return self.post_process_urls(urlpatterns)


application = OverriddenCheckoutApplication()
