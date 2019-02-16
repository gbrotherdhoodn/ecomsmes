import datetime

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from oscar.core.loading import get_class, get_model

ReportGenerator = get_class('dashboard.reports.reports', 'ReportGenerator')
ReportCSVFormatter = get_class('dashboard.reports.reports',
                               'ReportCSVFormatter')
ReportHTMLFormatter = get_class('dashboard.reports.reports',
                                'ReportHTMLFormatter')
Order = get_model('order', 'Order')


class WithdrawalReportCSVFormatter(ReportCSVFormatter):
    filename_template = 'withdrawal-%s.csv'

    def generate_csv(self, response, orders):
        writer = self.get_csv_writer(response)
        header_row = [(_('Order Transaction'), 5),
                      (_('Ipay Fee'), 7),
                      (_('GDN Fee'), 1),
                      (_('KGX Fee'), 1),
                      (_('Merchant Fee'), 4)]
        arrange_row = []
        for h in header_row:
            arrange_row.append(h[0])
            for i in range(h[1]):
                arrange_row.append('')
        writer.writerow(arrange_row)
        header_row_2 = [
            _("Order number"),
            _("Order Amount"),
            _("Shipping Cost"),
            _("Product Promo"),
            _("Shiping Promo"),
            _("Total Order"),
            _("Payment Method"),
            _("% Based"),
            _("Bank Fee"),
            _("Amount Base"),
            _("iPay Cost"),
            _("Tax for iPay (VAT)"),
            _("Service Tax (PPh23)"),
            _("Total iPay Cost"),
            _("% Based"),
            _("Total GDN Fee"),
            _("KGX Fee"),
            _("Promo Shipping"),
            _("Total Order"),
            _("Total iPay Cost"),
            _("Total GDN Cost"),
            _("Income Transferred by iPay88"),
            _("Remarks"),
        ]
        writer.writerow(header_row_2)
        for order in orders:
            sources = order.sources.last()
            shipping_discount = order.shipping_discounts.last()
            row = [
                order.number,
                order.total_before_voucher or '-',
                order.kgx_fee or '-',
                order.voucher.amount if order.voucher and order.voucher.category != 'Shipping' else '-',
                shipping_discount.amount if shipping_discount else '-',
                order.total_incl_tax or '-',
                sources.source_type if sources else '-',
                sources.source_type.percent_fee if sources else '-',
                sources.source_type.bank_fee if sources else '-',
                sources.source_type.amount_fee if sources else '-',
                order.ipay_cost or '-',
                order.tax_vat or '-',
                order.tax_pph23 or '-',
                order.total_ipay_cost or '-',
                order.gdn_fee or '-',
                order.total_gdn_fee or '-',
                order.kgx_fee or '-',
                shipping_discount.amount if shipping_discount else '-',
                order.total_incl_tax or '-',
                order.total_ipay_cost or '-',
                order.total_gdn_fee or '-',
                order.total_income or '-',
                _('Include shipping cost')
            ]
            writer.writerow(row)

        writer.writerow(['Summary'])

        total_order_before_voucher = sum([getattr(o, 'total_before_voucher') for o in orders])
        total_order_incl_tax = sum([getattr(o, 'total_incl_tax') for o in orders])
        total_kgx_fee = sum([getattr(o, 'kgx_fee') for o in orders])
        total_ipay_cost = sum([getattr(o, 'ipay_cost') for o in orders])
        final_total_ipay_cost = sum([getattr(o, 'total_ipay_cost') for o in orders])
        total_order_gdn_fee = sum([getattr(o, 'total_gdn_fee') for o in orders])
        total_order_income_tf = sum([getattr(o, 'total_income') for o in orders])
        writer.writerow([
            '', total_order_before_voucher, total_kgx_fee, '', '', total_order_incl_tax,  '', '', '', '',
            total_ipay_cost, '', '', final_total_ipay_cost, '', total_order_gdn_fee, total_kgx_fee, '',
            total_order_incl_tax, final_total_ipay_cost, total_order_gdn_fee, total_order_income_tf
        ])

    def filename(self, **kwargs):
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        date_str = _('all')
        if start_date:
            date_str = _(f'from {start_date}')
        if end_date:
            date_str = _(f'until {end_date}')
        if start_date and end_date:
            date_str = _(f'between {start_date} and {end_date}')
        return self.filename_template % date_str


class WithdrawalReportHTMLFormatter(ReportHTMLFormatter):
    filename_template = 'dashboard/reports/partials/withdrawal_report.html'


class WithdrawalReportGenerator(ReportGenerator):
    code = 'withdrawal_report'
    description = _("Withdrawal")
    date_range_field_name = 'date_placed'

    formatters = {
        'CSV_formatter': WithdrawalReportCSVFormatter,
        'HTML_formatter': WithdrawalReportHTMLFormatter,
    }

    def generate(self):
        order_status = [settings.ORDER_STATUS_PAID, settings.ORDER_STATUS_SHIPPED, settings.ORDER_STATUS_COMPLETED]
        qs = Order.objects.filter(status__in=order_status)

        if self.start_date:
            qs = qs.filter(date_placed__gte=self.start_date)
        if self.end_date:
            qs = qs.filter(
                date_placed__lt=self.end_date + datetime.timedelta(days=1))
        if self.order_number:
            qs = qs.filter(number=self.order_number)

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(qs, **additional_data)

    def is_available_to(self, user):
        return user.is_staff
