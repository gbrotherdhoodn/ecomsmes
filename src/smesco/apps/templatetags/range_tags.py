from django import template

register = template.Library()


@register.simple_tag
def get_destination_name(type, id):
    from apps.address.models import State, District, Subdistrict, Village

    if type == 'state':
        result = State.objects.get(id=id)
    elif type == 'district':
        result = District.objects.get(id=id)
    elif type == 'subdistrict':
        result = Subdistrict.objects.get(id=id)
    elif type == 'village':
        result = Village.objects.get(id=id)
    elif type == 'allarea':
        result = 'All Destination'

    return result
