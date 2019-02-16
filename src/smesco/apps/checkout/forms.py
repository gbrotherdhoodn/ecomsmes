from oscar.core.loading import get_model
from oscar.forms.mixins import PhoneNumberMixin
from apps.address.forms import AbstractAddressForm
from apps.address.models import State, District, Subdistrict, Village, UserAddress


class ShippingAddressForm(PhoneNumberMixin, AbstractAddressForm):

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
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

    class Meta:
        model = get_model('order', 'shippingaddress')
        fields = [
            'title', 'first_name', 'last_name',
            'line1', 'province', 'regency_district', 'subdistrict', 'village',
            'postcode', 'country',
            'phone_number', 'notes'
        ]


# The BillingAddress form is in oscar.apps.payment.forms
