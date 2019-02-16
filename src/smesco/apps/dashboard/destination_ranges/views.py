from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView)
from oscar.core.loading import get_class, get_model

from apps.address.models import State, District, Subdistrict

RangeDestination = get_model('offer', 'RangeDestination')
RangeDestinationForm = get_class('apps.dashboard.destination_ranges.forms', 'RangeDestinationForm')


class RangeListView(ListView):
    model = RangeDestination
    context_object_name = 'ranges'
    template_name = 'dashboard/destination_ranges/range_list.html'
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE


class RangeCreateView(CreateView):
    model = RangeDestination
    template_name = 'dashboard/destination_ranges/range_form.html'
    form_class = RangeDestinationForm

    def get_success_url(self):
        msg = render_to_string(
            'dashboard/destination_ranges/messages/range_saved.html',
            {'range': self.object})
        messages.success(self.request, msg, extra_tags='safe noicon')
        return reverse('dashboard:destination-range-list')

    def get_context_data(self, **kwargs):
        ctx = super(RangeCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _("Create destination range")
        ctx['provinces'] = State.objects.all()
        ctx['districts'] = District.objects.all()
        ctx['subdistricts'] = Subdistrict.objects.all()
        return ctx


class RangeUpdateView(UpdateView):
    model = RangeDestination
    template_name = 'dashboard/destination_ranges/range_form.html'
    form_class = RangeDestinationForm

    def get_success_url(self):
        msg = render_to_string(
            'dashboard/destination_ranges/messages/range_saved.html',
            {'range': self.object})
        messages.success(self.request, msg, extra_tags='safe noicon')
        return reverse('dashboard:destination-range-list')

    def get_context_data(self, **kwargs):
        ctx = super(RangeUpdateView, self).get_context_data(**kwargs)
        ctx['range'] = self.object
        ctx['title'] = self.object.name
        ctx['provinces'] = State.objects.all()
        ctx['districts'] = District.objects.all()
        ctx['subdistricts'] = Subdistrict.objects.all()
        return ctx


class RangeDeleteView(DeleteView):
    model = RangeDestination
    template_name = 'dashboard/destination_ranges/range_delete.html'
    context_object_name = 'range'

    def get_success_url(self):
        messages.warning(self.request, _("Destination Range deleted"))
        return reverse('dashboard:destination-range-list')
