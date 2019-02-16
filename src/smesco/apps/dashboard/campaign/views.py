from django.urls import reverse_lazy, reverse
from django.views.generic import (CreateView, DeleteView, UpdateView, DetailView)
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from .forms import BannerForm, BannerSearchForm, BannerMiniForm, BannerMiniSearchForm, \
    EndorsementForm, EndorsementSearchForm
from .tables import BannerTable, BannerMiniTable, EndorsementTable
from django_tables2 import SingleTableView
from oscar.core.loading import get_model

Banner = get_model('campaign', 'Banner')
BannerMini = get_model('campaign', 'BannerMini')
Endorsement = get_model('campaign', 'Endorsement')

# ===============================================
#
#                    BANNER
#
# ===============================================


# ============
# CREATE VIEWS
# ============
class BannerCreateView(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/banner/banner_form.html'
    success_url = reverse_lazy('dashboard:banner-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner created successfully"))
        return super(BannerCreateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(BannerCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _("Create Banner")
        return ctx


# ============
# UPDATE VIEWS
# ============
class BannerUpdateView(UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/banner/banner_form.html'
    success_url = reverse_lazy('dashboard:banner-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner updated successfully"))
        return super(BannerUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(BannerUpdateView, self).get_context_data(**kwargs)
        ctx['banner'] = self.object
        ctx['title'] = self.object.title
        return ctx


# ============
# DELETE VIEWS
# ============
class BannerDeleteView(DeleteView):
    model = Banner
    context_object_name = 'banner'
    template_name = 'dashboard/banner/banner_delete.html'
    success_url = reverse_lazy('dashboard:banner-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner deleted"))
        return reverse('dashboard:banner-list')


# ============
# LIST VIEWS
# ============
class BannerListView(SingleTableView):
    model = Banner
    table_class = BannerTable
    form_class = BannerSearchForm
    context_table_name = 'banners'
    template_name = 'dashboard/banner/banner_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(BannerListView, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx

    def get_description(self, form):
        if form.is_valid() and any(form.cleaned_data.values()):
            return _('Banners search results')
        return _('Banners')

    def get_table(self, **kwargs):
        table = super(BannerListView, self).get_table(**kwargs)
        table.caption = self.get_description(self.form)
        return table

    def get_table_pagination(self, table):
        return dict(per_page=20)

    def get_queryset(self):
        queryset = self.model.objects.all()
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data
        if data['title']:
            queryset = queryset.filter(title__icontains=data['title'])
        return queryset


# ============
# DETAIL VIEWS
# ============
class BannerDetailView(DetailView):
    model = Banner
    context_object_name = 'txn'
    template_name = 'dashboard/banner/banner_detail.html'


# ===============================================
#
#                  BANNER MINI
#
# ===============================================

# ============
# CREATE VIEWS
# ============
class BannerMiniCreateView(CreateView):
    model = BannerMini
    form_class = BannerMiniForm
    template_name = 'dashboard/banner_mini/banner_mini_form.html'
    success_url = reverse_lazy('dashboard:banner-mini-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner mini created successfully"))
        return super(BannerMiniCreateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(BannerMiniCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _("Create Banner Mini")
        return ctx


# ============
# UPDATE VIEWS
# ============
class BannerMiniUpdateView(UpdateView):
    model = BannerMini
    form_class = BannerMiniForm
    template_name = 'dashboard/banner_mini/banner_mini_form.html'
    success_url = reverse_lazy('dashboard:banner-mini-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner mini updated successfully"))
        return super(BannerMiniUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(BannerMiniUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = self.object.title
        return ctx


# ============
# DELETE VIEWS
# ============
class BannerMiniDeleteView(DeleteView):
    model = BannerMini
    context_object_name = 'banner_mini'
    template_name = 'dashboard/banner_mini/banner_mini_delete.html'
    success_url = reverse_lazy('dashboard:banner-mini-list')

    def get_success_url(self):
        messages.info(self.request, _("Banner mini deleted"))
        return reverse('dashboard:banner-mini-list')


# ============
# LIST VIEWS
# ============
class BannerMiniListView(SingleTableView):
    model = BannerMini
    table_class = BannerMiniTable
    form_class = BannerMiniSearchForm
    context_table_name = 'banner_minis'
    template_name = 'dashboard/banner_mini/banner_mini_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(BannerMiniListView, self).get_context_data(**kwargs)
        max_banner_mini = getattr(settings, 'MAX_BANNER_MINI', None) | 4
        ctx['form'] = self.form
        ctx['max_banner_mini'] = max_banner_mini
        return ctx

    def get_description(self, form):
        if form.is_valid() and any(form.cleaned_data.values()):
            return _('Banner mini search results')
        return _('Banner Mini')

    def get_table(self, **kwargs):
        table = super(BannerMiniListView, self).get_table(**kwargs)
        table.caption = self.get_description(self.form)
        return table

    def get_table_pagination(self, table):
        return dict(per_page=20)

    def get_queryset(self):
        queryset = self.model.objects.all()
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data
        if data['title']:
            queryset = queryset.filter(title__icontains=data['title'])
        return queryset


# ============
# DETAIL VIEWS
# ============
class BannerMiniDetailView(DetailView):
    model = BannerMini
    context_object_name = 'txn'
    template_name = 'dashboard/banner_mini/banner_mini_detail.html'


# ===============================================
#
#                    ENDORSEMENT
#
# ===============================================

# ============
# CREATE VIEWS
# ============
class EndorsementCreateView(CreateView):
    model = Endorsement
    form_class = EndorsementForm
    template_name = 'dashboard/endorsements/endorsement_form.html'
    success_url = reverse_lazy('dashboard:endorsement-list')

    def get_success_url(self):
        messages.info(self.request, _("Endorsement created successfully"))
        return super(EndorsementCreateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(EndorsementCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _("Create Endorsement")
        return ctx


# ============
# UPDATE VIEWS
# ============
class EndorsementUpdateView(UpdateView):
    model = Endorsement
    form_class = EndorsementForm
    template_name = 'dashboard/endorsements/endorsement_form.html'
    success_url = reverse_lazy('dashboard:endorsement-list')

    def get_success_url(self):
        messages.info(self.request, _("Endorsement updated successfully"))
        return super(EndorsementUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super(EndorsementUpdateView, self).get_context_data(**kwargs)
        ctx['endorsement'] = self.object
        ctx['name'] = self.object.name
        return ctx


# ============
# DELETE VIEWS
# ============
class EndorsementDeleteView(DeleteView):
    model = Endorsement
    context_object_name = 'endorsement'
    template_name = 'dashboard/endorsements/endorsement_delete.html'
    success_url = reverse_lazy('dashboard:endorsement-list')

    def get_success_url(self):
        messages.info(self.request, _("Endorsement deleted"))
        return reverse('dashboard:endorsement-list')


# ============
# LIST VIEWS
# ============
class EndorsementListView(SingleTableView):
    model = Endorsement
    table_class = EndorsementTable
    form_class = EndorsementSearchForm
    context_table_name = 'endorsements'
    template_name = 'dashboard/endorsements/endorsement_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(EndorsementListView, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx

    def get_description(self, form):
        if form.is_valid() and any(form.cleaned_data.values()):
            return _('Endorsements search results')
        return _('Endorsements')

    def get_table(self, **kwargs):
        table = super(EndorsementListView, self).get_table(**kwargs)
        table.caption = self.get_description(self.form)
        return table

    def get_table_pagination(self, table):
        return dict(per_page=20)

    def get_queryset(self):
        queryset = self.model.objects.all()
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset
        data = self.form.cleaned_data
        if data['name']:
            queryset = queryset.filter(name__icontains=data['name'])
        return queryset


# ============
# DETAIL VIEWS
# ============
class EndorsementDetailView(DetailView):
    model = Endorsement
    context_object_name = 'txn'
    template_name = 'dashboard/endorsements/endorsement_detail.html'
