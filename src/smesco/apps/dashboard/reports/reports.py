from oscar.apps.dashboard.reports.reports import ReportGenerator as OriginalReportGenerator
from django.utils.translation import ugettext_lazy as _


class ReportGenerator(OriginalReportGenerator):
    def __init__(self, **kwargs):
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.order_number = kwargs.get('order_number')
        formatter_name = '%s_formatter' % kwargs['formatter']
        self.formatter = self.formatters[formatter_name]()

    def report_description(self):
        date_str = _('all')
        if self.start_date:
            date_str = _(f'from {self.start_date}')
        if self.end_date:
            date_str = _(f'until {self.end_date}')
        if self.start_date and self.end_date:
            date_str = _(f'between {self.start_date} and {self.end_date}')
        return _(f'{self.description} {date_str}')
