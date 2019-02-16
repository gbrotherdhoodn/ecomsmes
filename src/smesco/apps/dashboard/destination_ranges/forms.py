from django import forms
from oscar.core.loading import get_model
from apps.offer.models import DESTINATION_TYPE_CHOICES
from django_select2.forms import Select2Widget

RangeDestination = get_model('offer', 'RangeDestination')


class RangeDestinationForm(forms.ModelForm):
    tuple_list = list(DESTINATION_TYPE_CHOICES)
    tuple_list.pop(4)
    destination_type_options = tuple(tuple_list)
    destination_type = forms.ChoiceField(
        required=True,
        choices=destination_type_options,
        label="Destination Type",
        widget=Select2Widget(attrs={'onchange': "oscar.destinationRange.getDestination(this);"})
    )

    destination_name = forms.CharField(label="Destination Name", widget=Select2Widget)

    class Meta:
        model = RangeDestination
        fields = [
            'name', 'description', 'destination_type', 'destination_name', 'destination_id',
        ]
