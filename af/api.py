import json

from django.http import HttpResponse
from af.functions import ok_json, model_to_dict_safe, bad_json
from af.models import Area, Asset


def view(request):
    if 'a' in request.GET:
        action = request.GET['a']
        if action == 'af':
            if Asset.objects.filter(code=request.GET['c']).exists():
                asset = Asset.objects.get(code=request.GET['c'])
                d = model_to_dict_safe(asset, exclude=['entry_date'])
                d['type'] = asset.type.name
                x = asset.area
                d['area'] = {'id': x.id, 'nombre': x.name, 'responsable': x.responsible}
                return ok_json(data=d)
            else:
                return bad_json(mensaje=u'Code does not exists.')

        elif action == 'afareas':
            areas = Area.objects.all().order_by('departamento__nombre')
            lista = []
            for x in areas:
                lista.append(
                    {'id': x.id, 'nombre': x.departamento.nombre, 'responsable': x.responsable.nombre_completo()})
            return ok_json(data=lista)

        elif action == 'afarea':
            area = Area.objects.get(pk=request.GET['area'])
            activos = Asset.objects.filter(area=area)
            lista = []
            for x in activos:
                d = model_to_dict_safe(x, exclude=['fechaingreso'])
                d['tipo'] = x.tipo.nombre
                lista.append(d)
            return ok_json(data=lista)

    return HttpResponse(json.dumps(['FIXED ASSETS', 'GMSOFT (C) All rights reserved']), content_type="application/json")
