from django.http import Http404, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.reports.views import IndexView as OriginalIndexView


class IndexView(OriginalIndexView):

    def _get_generator(self, form):
        code = form.cleaned_data['report_type']
        repo = self.generator_repository()
        generator_cls = repo.get_generator(code)
        if not generator_cls:
            raise Http404()
        download = form.cleaned_data['download']
        formatter = 'CSV' if download else 'HTML'
        return generator_cls(start_date=form.cleaned_data['date_from'],
                             end_date=form.cleaned_data['date_to'],
                             order_number=form.cleaned_data['order_number'],
                             formatter=formatter)

    def get(self, request, *args, **kwargs):
        if 'report_type' in request.GET:
            form = self.report_form_class(request.GET)
            if form.is_valid():
                generator = self._get_generator(form)
                if not generator.is_available_to(request.user):
                    return HttpResponseForbidden(_("You do not have access to"
                                                   " this report"))
                report = generator.generate()
                if form.cleaned_data['download']:
                    return report
                else:
                    self.set_list_view_attrs(generator, report)
                    context = self.get_context_data(object_list=self.queryset)
                    context['form'] = form
                    context['description'] = generator.report_description()
                    context['qs'] = self.queryset
                    return self.render_to_response(context)
        else:
            form = self.report_form_class()
        return TemplateResponse(request, self.template_name, {'form': form})
