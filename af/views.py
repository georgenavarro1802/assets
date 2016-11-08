#! /usr/bin/env python
# -*- coding: utf-8 -*-
import string
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from af.functions import NOMBRE_INSTITUCION


def addUserData(request, data):
    data['usuario'] = request.user
    data['currenttime'] = datetime.now()
    data['nombreinstitucion'] = NOMBRE_INSTITUCION


@login_required(redirect_field_name='ret', login_url='/login')
def index(request):
    data = {'title': 'Fixed Assets - ' + NOMBRE_INSTITUCION,
            'link': 'home'}
    addUserData(request, data)
    return render_to_response("index.html", data)


def login_user(request):
    if request.method == 'POST':
        user = authenticate(username=string.lower(request.POST['username']), password=request.POST['password'])
        if user is not None:
            if not user.is_active:
                return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=3")
            else:
                login(request, user)
                return HttpResponseRedirect(request.POST['ret'])
        else:
            return HttpResponseRedirect("/login?ret=" + request.POST['ret'] + "&error=1")
    else:
        ret = '/'
        if 'ret' in request.GET:
            ret = request.GET['ret']
        return render_to_response("login.html",
                                  {
                                      "title": "Login", "return_url": ret,
                                      "error": request.GET['error'] if 'error' in request.GET else "",
                                      "request": request,
                                      "nombreinstitucion": NOMBRE_INSTITUCION,
                                      "currenttime": datetime.now()
                                  })


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")
