from collections import OrderedDict
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from oscar.core.compat import UnicodeCSVWriter
from oscar.core.utils import format_datetime

from oscar.apps.dashboard.users.views import IndexView as CoreIndexView


class IndexView(CoreIndexView):
    actions = ('make_active', 'make_inactive', 'download_selected_users', )

    def is_csv_download(self):
        return self.request.GET.get('response_format', None) == 'csv'

    def get_paginate_by(self, queryset):
        return None if self.is_csv_download() else self.paginate_by

    def get_download_filename(self, request):
        return 'customers.csv'

    def render_to_response(self, context, **response_kwargs):
        if self.is_csv_download():
            return self.download_selected_users(
                self.request,
                context['object_list'])
        return super(IndexView, self).render_to_response(
            context, **response_kwargs)

    def download_selected_users(self, request, users):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' \
                                          % self.get_download_filename(request)
        writer = UnicodeCSVWriter(open_file=response)

        meta_data = (('no', _('User Id')),
                     ('email', _('User Email')),
                     ('name', _('User Name')),
                     ('telp', _('Telephone')),
                     ('birthdate', _('Birth Of Date')),
                     ('register_date', _('Registered Date')),
                     ('shipping_address_name', _('Default Address Shipping')),
                     )
        columns = OrderedDict()
        for k, v in meta_data:
            columns[k] = v

        writer.writerow(columns.values())
        for user in users:
            row = columns.copy()
            row['no'] = user.id
            row['email'] = user.email
            row['name'] = user.get_full_name()
            row['telp'] = user.phone
            row['birthdate'] = user.birthdate
            row['register_date'] = format_datetime(user.date_joined, 'DATETIME_FORMAT')
            default_address = user.addresses.filter(is_default_for_shipping=True).last()
            if default_address:
                row['shipping_address_name'] = '\n'.join(default_address.active_address_fields())
            else:
                row['shipping_address_name'] = ''
            writer.writerow(row.values())
        return response
