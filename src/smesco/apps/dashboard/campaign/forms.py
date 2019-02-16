from string import Template

from django import forms
from django.conf import settings
from django.forms import ImageField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from oscar.forms import widgets
from oscar.core.loading import get_model

Banner = get_model('campaign', 'Banner')
BannerMini = get_model('campaign', 'BannerMini')
Endorsement = get_model('campaign', 'Endorsement')


class PictureWidget(widgets.ImageInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = Template("""<img src="$link" style="max-width:320px;height:auto;"/>""")
        return mark_safe(html.substitute(link=f"{settings.MEDIA_URL}{self.attrs.get('value')}"))


class BannerForm(forms.ModelForm):
    photo_desktop = ImageField(widget=PictureWidget, required=True)
    photo_mobile = ImageField(widget=PictureWidget, required=True)
    number = forms.IntegerField(required=True, label=_("Priority"))
    url = forms.URLField(required=True, label=_("Redirect Url"))
    valid_from = forms.DateTimeField(required=True, label=_('Valid From'), widget=widgets.DateTimePickerInput())
    valid_until = forms.DateTimeField(required=True, label=_('Valid Until'), widget=widgets.DateTimePickerInput())

    class Meta:
        model = Banner
        fields = ('image_desktop', 'image_mobile', 'title', 'description', 'number', 'url', 'valid_from', 'valid_until',
                  'published')
        readonly_fields = ('photo_desktop', 'photo_mobile',)

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            self.base_fields['photo_desktop'] = ImageField(widget=
                                                           PictureWidget({'value': kwargs.get('instance').image_desktop}),
                                                           required=False)
            self.base_fields['photo_mobile'] = ImageField(widget=
                                                          PictureWidget({'value': kwargs.get('instance').image_mobile}),
                                                          required=False)
        else:
            if self.base_fields.get('photo_desktop'):
                self.base_fields.pop('photo_desktop')
                self.base_fields.pop('photo_mobile')
        super(BannerForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        if not self.instance.id:
            if Banner.objects.filter(title=self.cleaned_data['title']).exists():
                raise forms.ValidationError('Banner with this Name already exists.')
        else:
            if Banner.objects.filter(title__icontains=self.cleaned_data['title']).exclude(id=self.instance.id):
                raise forms.ValidationError('Banner with this Name already exists.')

        return self.cleaned_data['title']

    def save(self, *args, **kwargs):
        exist_banner = Banner.objects.filter(number=self.cleaned_data['number'])
        if exist_banner:
            update_banner = Banner.objects.filter(number__gte=self.cleaned_data['number']).order_by('number')
            for update in update_banner:
                update.number = update.number + 1
                update.save()
        return super(BannerForm, self).save(*args, **kwargs)


class BannerMiniForm(forms.ModelForm):
    photo = ImageField(widget=PictureWidget, required=True)
    url = forms.URLField(required=True, label=_("Redirect Url"))

    class Meta:
        model = BannerMini
        fields = ('image', 'photo', 'title', 'description', 'url', 'published')
        readonly_fields = ('photo',)

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            self.base_fields['photo'] = ImageField(widget=PictureWidget({'value': kwargs.get('instance').image}),
                                                   required=False)
        else:
            if self.base_fields.get('photo'):
                self.base_fields.pop('photo')
        super(BannerMiniForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        if not self.instance.id:
            if BannerMini.objects.filter(self.cleaned_data['title']).exists():
                raise forms.ValidationError('BannerMini with this Name already exists.')
        else:
            if BannerMini.objects.filter(title__icontains=self.cleaned_data['title']).exclude(id=self.instance.id):
                raise forms.ValidationError('BannerMini with this Name already exists.')

        return self.cleaned_data['title']

    def save(self, *args, **kwargs):
        exist_banner = BannerMini.objects.filter(sort_priority=0)
        if exist_banner and not self.instance.id:
            update_banner = BannerMini.objects.filter(sort_priority__gte=0)\
                .order_by('sort_priority')
            for update in update_banner:
                update.sort_priority = update.sort_priority + 1
                update.save()
        return super(BannerMiniForm, self).save(*args, **kwargs)


class EndorsementForm(forms.ModelForm):
    photo = ImageField(widget=PictureWidget, required=True)
    sort_priority = forms.IntegerField(required=True, label=_("Sort Priority"))
    url = forms.URLField(required=True, label=_("Social Media Url"))
    valid_from = forms.DateTimeField(required=True, label=_('Valid From'), widget=widgets.DateTimePickerInput())
    valid_until = forms.DateTimeField(required=True, label=_('Valid Until'), widget=widgets.DateTimePickerInput())

    class Meta:
        model = Endorsement
        fields = ('image', 'photo', 'name', 'description', 'sort_priority', 'url',
                  'valid_from', 'valid_until', 'published')
        readonly_fields = ('photo',)

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            self.base_fields['photo'] = ImageField(widget=PictureWidget({'value': kwargs.get('instance').image}),
                                                   required=False)
        else:
            if self.base_fields.get('photo'):
                self.base_fields.pop('photo')
        super(EndorsementForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        if not self.instance.id:
            if Endorsement.objects.filter(name=self.cleaned_data['name']).exists():
                raise forms.ValidationError('Endorsement with this Name already exists.')
        else:
            if Endorsement.objects.filter(name__icontains=self.cleaned_data['name']).exclude(id=self.instance.id):
                raise forms.ValidationError('Endorsement with this Name already exists.')

        return self.cleaned_data['name']

    def save(self, *args, **kwargs):
        exist_banner = Endorsement.objects.filter(sort_priority=self.cleaned_data['sort_priority'])
        if exist_banner:
            update_banner = Endorsement.objects.filter(sort_priority__gte=self.cleaned_data['sort_priority'])\
                .order_by('sort_priority')
            for update in update_banner:
                update.sort_priority = update.sort_priority + 1
                update.save()
        return super(EndorsementForm, self).save(*args, **kwargs)


class BannerSearchForm(forms.Form):
    title = forms.CharField(required=False, label=_("Title"))


class BannerMiniSearchForm(forms.Form):
    title = forms.CharField(required=False, label=_("Title"))


class EndorsementSearchForm(forms.Form):
    name = forms.CharField(required=False, label=_("Title"))
