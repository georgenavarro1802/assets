#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime

from decimal import Decimal
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.http import HttpResponse


NOMBRE_INSTITUCION = 'GM SOFT'

DEFAULT_PASSWORD = 'assets'

MENSAJES_ERROR = [
    u'Permiso denegado.',
    u'No tiene permiso para modificar la inscripcion.',
    u'No tiene permiso para realizar esta accion.'
]


def generate_file_name(nombre, original):
    ext = ""
    if original.find(".") > 0:
        ext = original[original.rfind("."):]
    fecha = datetime.now().date()
    hora = datetime.now().time()
    return nombre + fecha.year.__str__() + fecha.month.__str__() + fecha.day.__str__() + \
           hora.hour.__str__() + hora.minute.__str__() + hora.second.__str__() + ext


class MiPaginador(Paginator):

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(MiPaginador, self).__init__(object_list, per_page, orphans=orphans,
                                          allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left < 1:
            left = 1
        if right > self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right + 1)
        self.primera_pagina = True if left > 1 else False
        self.ultima_pagina = True if right < self.num_pages else False
        self.ellipsis_izquierda = left - 1
        self.ellipsis_derecha = right + 1


def convertir_fecha(s):
    try:
        return datetime(int(s[-4:]), int(s[3:5]), int(s[:2]))
    except:
        return datetime.now()


def model_to_dict_safe(m, exclude=None):
    if not exclude:
        exclude = []
    d = model_to_dict(m, exclude=exclude)
    for x, y in d.iteritems():
        if type(y) == Decimal:
            d[x] = float(y)
    return d


def url_back(request, mensaje=None):
    url = request.META['HTTP_REFERER'].split('/')[-1:][0]
    if 'mensj=' in url:
        url = url[:(url.find('mensj') - 1)]
    if mensaje:
        if '?' in url:
            url += "&mensj=" + mensaje
        else:
            url += "?mensj=" + mensaje
    return url


def mensaje_excepcion(mensaje):
    if mensaje not in MENSAJES_ERROR:
        mensaje = MENSAJES_ERROR[0]
    return mensaje


def bad_json(mensaje=None, error=None, extradata=None):
    data = {'result': 'bad'}
    if mensaje:
        data.update({'mensaje': mensaje})
    if error:
        if error == 0:
            data.update({"mensaje": "Incorrect request"})
        elif error == 1:
            data.update({"mensaje": "Error saving data"})
        elif error == 2:
            data.update({"mensaje": "Error deleting data"})
        elif error == 3:
            data.update({"mensaje": "Error getting data"})
        elif error == 4:
            data.update({"mensaje": "You dont have permission to perform this action"})
        elif error == 5:
            data.update({"mensaje": "Error generating the information"})
        else:
            data.update({"mensaje": "System error"})
    if extradata:
        data.update(extradata)
    return HttpResponse(json.dumps(data), content_type="application/json")


def ok_json(data=None, simple=None):
    if data:
        if not simple:
            if 'result' not in data.keys():
                data.update({"result": "ok"})
    else:
        data = {"result": "ok"}
    return HttpResponse(json.dumps(data), content_type="application/json")
