from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from oscar.app import application
from oscar.core.loading import get_class
from apps.campaign.app import application as campaign
from apps.payment.views import payment_notifications, payment_response
from apps.campaign.views import contact_us_email_view


list_states = get_class('apps.address.views', 'load_states')
list_districts = get_class('apps.address.views', 'load_districts')
list_subdistricts = get_class('apps.address.views', 'load_subdistricts')
list_villages = get_class('apps.address.views', 'load_villages')
link_activate = get_class('apps.customer.views', 'activate')
get_postcode = get_class('apps.address.views', 'get_postcode')
change_order_status = get_class('apps.customer.views', 'change_order_status')
offer_app = get_class('offer.app', 'application')

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('admin/statuscheck/', include('celerybeat_status.urls')),
    path('', application.urls),
    path('ajax/load-states/', list_states, name='load-address-states'),
    path('ajax/load-districts/', list_districts, name='load-address-districts'),
    path('ajax/load-subdistricts/', list_subdistricts, name='load-address-subdistricts'),
    path('ajax/load-villages/', list_villages, name='load-address-villages'),
    path('ajax/get-postcode/', get_postcode, name='load-address-postcode'),
    path('accounts/activate/<slug:uidb64>/<slug:token>/', link_activate, name='activate'),
    path('accounts/change-order-status/', change_order_status, name='change-order-status'),
    path('payment/<int:order_number>/notification/', payment_notifications, name='payment-notification'),
    path('payment/<int:order_number>/response/', payment_response, name='payment-response'),
    path('campaign/', campaign.urls),
    path('contact-us/', contact_us_email_view, name='contact-us')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


