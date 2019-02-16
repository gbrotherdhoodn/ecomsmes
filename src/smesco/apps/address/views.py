from .models import State, District, Subdistrict, Village
from django.shortcuts import render
from django.http import HttpResponse


def load_states(request):
    country_id = request.GET.get('param')
    states = State.objects.filter(country_id=country_id).order_by('name')
    return render(request, 'partials/dropdown_list_options.html', {'list': states})


def load_districts(request):
    state_id = request.GET.get('param')
    districts = District.objects.filter(state_id=state_id).order_by('name')
    return render(request, 'partials/dropdown_list_options.html', {'list': districts})


def load_subdistricts(request):
    district_id = request.GET.get('param')
    subdistricts = Subdistrict.objects.filter(district_id=district_id).order_by('name')
    return render(request, 'partials/dropdown_list_options.html', {'list': subdistricts})


def load_villages(request):
    subdistrict_id = request.GET.get('param')
    villages = Village.objects.filter(subdistrict_id=subdistrict_id).order_by('name')
    return render(request, 'partials/dropdown_list_options.html', {'list': villages})


def get_postcode(request):
    village_id = request.GET.get('param')
    postcode = Village.objects.filter(id=village_id).last()
    return HttpResponse(postcode.postcode if postcode else None, content_type='application/json')

