from django import forms
from django.conf import settings
from oscar.forms.mixins import PhoneNumberMixin
from django.utils.translation import ugettext_lazy as _
from oscar.apps.address.forms import AbstractAddressForm
from phonenumber_field.formfields import PhoneNumberField
from .models import State, District, Subdistrict, Village, UserAddress


class AbstractAddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(AbstractAddressForm, self).__init__(*args, **kwargs)
        field_names = (set(self.fields) &
                       set(getattr(settings, 'OSCAR_REQUIRED_ADDRESS_FIELDS', None)))
        for field_name in field_names:
            self.fields[field_name].required = True

        self.fields['country'].widget = forms.HiddenInput()
        self.fields['line1'].widget = forms.Textarea()


class UserAddressForm(PhoneNumberMixin, AbstractAddressForm):
    first_name = forms.CharField(required=True, label=_('Nama Depan'))
    last_name = forms.CharField(required=True, label=_('Nama Belakang'))
    phone_number = PhoneNumberField(label=_("Nomor Telepon"), required=False,
                                    help_text=_("Jika dalam kondisi diharuskan untuk konfirmasi alamat tujuan"))
    notes = forms.CharField(required=False, widget=forms.Textarea, label=_('Instruksi'),
                            help_text=_("Beritahu kami jika ada catatan dalam pengiriman"))

    class Meta:
        model = UserAddress
        fields = [
            'first_name', 'last_name', 'line1', 'province',
            'regency_district', 'subdistrict', 'village',
            'postcode', 'country', 'phone_number', 'notes'
        ]

    def __init__(self, user, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.instance.user = user
        if user.is_authenticated:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone_number'].initial = user.phone
        self.fields['province'].queryset = State.objects.none()
        self.fields['regency_district'].queryset = District.objects.none()
        self.fields['subdistrict'].queryset = Subdistrict.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        if 'country' in self.data:
            try:
                country_id = self.data.get('country')
                self.fields['province'].queryset = State.objects.filter(country_id=country_id).order_by('name')

                state_id = int(self.data.get('province'))
                self.fields['regency_district'].queryset = District.objects.filter(state_id=state_id).order_by('name')

                district_id = int(self.data.get('regency_district'))
                self.fields['subdistrict'].queryset = Subdistrict.objects.filter(district_id=district_id).order_by('name')

                subdistrict_id = int(self.data.get('subdistrict'))
                self.fields['village'].queryset = Village.objects.filter(subdistrict_id=subdistrict_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['province'].queryset = State.objects.filter(country_id=self.instance.country_id)
            self.fields['regency_district'].queryset = District.objects.filter(state_id=self.instance.province_id)
            self.fields['subdistrict'].queryset = Subdistrict.objects.filter(district_id=self.instance.regency_district_id)
            self.fields['village'].queryset = Village.objects.filter(subdistrict_id=self.instance.subdistrict_id)
