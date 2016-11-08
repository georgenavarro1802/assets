import datetime

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from af.forms import AssetsForm
from af.functions import MiPaginador, bad_json, ok_json, generate_file_name, url_back, mensaje_excepcion
from af.models import Asset, Area, AssetType, AssetDepreciationTotal, AssetDepreciationDetail
from af.views import addUserData


def exists_depreciation_month(m):
    return AssetDepreciationTotal.objects.filter(date__month=m).exists()


def depreciation__total_month(m):
    if exists_depreciation_month(m):
        return AssetDepreciationTotal.objects.get(date__month=m).total_depreciated
    return 0


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Fixed Assets', 'link': 'assets'}
    addUserData(request, data)

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'add':
            f = AssetsForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    if f.cleaned_data['current_value'] > f.cleaned_data['initial_value']:
                        return bad_json(mensaje=u'Current value can not be greater than Initial Value')
                    if not Asset.objects.filter(code=f.cleaned_data['code']).exists():
                        asset = Asset(code=f.cleaned_data['code'],
                                      description=f.cleaned_data['description'],
                                      type=f.cleaned_data['type'],
                                      area=f.cleaned_data['area'],
                                      entry_date=f.cleaned_data['entry_date'],
                                      initial_value=f.cleaned_data['initial_value'],
                                      current_value=f.cleaned_data['current_value'],
                                      is_depreciable=f.cleaned_data['is_depreciable'])
                        asset.save()

                        if 'foto' in request.FILES:
                            newfile = request.FILES['foto']
                            newfile._name = generate_file_name("foto_", newfile._name)
                            asset.foto = newfile
                            asset.save()
                        return ok_json()
                    else:
                        return bad_json(mensaje=u'This asset code already exists.')
                except:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            asset = Asset.objects.get(pk=request.POST['id'])
            f = AssetsForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    if f.cleaned_data['current_value'] > f.cleaned_data['initial_value']:
                        return bad_json(mensaje=u'Current value can not be greater than Initial Value')
                    if not Asset.objects.filter(code=f.cleaned_data['code']).exclude(id=asset.id).exists():
                        asset.code = f.cleaned_data['code']
                        asset.description = f.cleaned_data['description']
                        asset.type = f.cleaned_data['type']
                        asset.area = f.cleaned_data['area']
                        asset.entry_date = f.cleaned_data['entry_date']
                        asset.initial_value = f.cleaned_data['initial_value']
                        asset.current_value = f.cleaned_data['current_value']
                        asset.is_depreciable = f.cleaned_data['is_depreciable']
                        asset.save()

                        if 'foto' in request.FILES:
                            newfile = request.FILES['foto']
                            newfile._name = generate_file_name("foto_", newfile._name)
                            asset.foto = newfile
                            asset.save()
                        return ok_json()
                    else:
                        return bad_json(mensaje=u'This asset code already exists.')
                except:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'delete':
            try:
                asset = Asset.objects.get(pk=request.POST['id'])
                asset.delete()
                return ok_json()
            except Exception:
                return bad_json(error=3)

        if action == 'depreciation':
            try:
                with transaction.atomic():
                    depreciation_total = AssetDepreciationTotal()
                    depreciation_total.save()

                    total_before = Decimal(0)
                    total_depreciated = Decimal(0)
                    for a in Asset.objects.filter(is_depreciable=True, current_value__gt=0):
                        value_to_depreciate = a.value_to_depreciate()
                        asset_depreciation = AssetDepreciationDetail(depreciation_total=depreciation_total,
                                                                     asset=a,
                                                                     before_value=a.current_value,
                                                                     rate=a.type.rate,
                                                                     depreciated_value=value_to_depreciate,
                                                                     area=a.area)
                        asset_depreciation.save()

                        # Update current value
                        if a.current_value - value_to_depreciate >= 0:
                            a.current_value -= value_to_depreciate
                        else:
                            a.current_value = Decimal(0)
                        a.save()

                    for ad in depreciation_total.assetdepreciationdetail_set.all():
                        total_before += ad.before_value
                        total_depreciated += ad.depreciated_value

                    depreciation_total.total_before = total_before
                    depreciation_total.total_depreciated = total_depreciated
                    depreciation_total.save()

                    return ok_json()
            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = 'Add Asset'
                    data['form'] = AssetsForm(initial={'entry_date': datetime.datetime.today()})
                    return render_to_response("assets/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = 'Edit Asset'
                    data['asset'] = asset = Asset.objects.get(pk=request.GET['id'])
                    data['form'] = AssetsForm(initial={'code': asset.code,
                                                       'description': asset.description,
                                                       'type': asset.type,
                                                       'area': asset.area,
                                                       'entry_date': asset.entry_date if asset.entry_date else datetime.datetime.today(),
                                                       'initial_value': asset.initial_value,
                                                       'current_value': asset.current_value,
                                                       'is_depreciable': asset.is_depreciable,
                                                       'foto': asset.foto})
                    return render_to_response("assets/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = 'Delete Asset'
                    data['asset'] = Asset.objects.get(pk=request.GET['id'])
                    return render_to_response("assets/delete.html", data)
                except Exception as ex:
                    pass

            elif action == 'depreciation':
                try:
                    data['title'] = 'Assets Depreciations'
                    return render_to_response("assets/depreciations.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))
        else:
            search = None
            area = None
            type = None
            depr = False    # Depreciation flag

            if 'd' in request.GET and int(request.GET['d']) > 0:
                depr = True

            if 'a' in request.GET and int(request.GET['a']) > 0:
                area = int(request.GET['a'])
            if 't' in request.GET and int(request.GET['t']) > 0:
                type = int(request.GET['t'])

            if 's' in request.GET:
                search = request.GET['s']

            assets = Asset.objects.all()
            if search:
                assets = assets.filter(Q(code__icontains=search) | Q(description__icontains=search))
            if area and type:
                assets = assets.filter(type__id=type, area__id=area)
            if area and not type:
                assets = assets.filter(area__id=area)
            if not area and type:
                assets = assets.filter(type__id=type)

            paging = MiPaginador(assets, 25)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(p)

            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['assets'] = page.object_list
            data['exists_depreciation_month'] = exists_depreciation_month(datetime.datetime.today().date().month)
            data['areas'] = Area.objects.all()
            data['areaid'] = int(request.GET['a']) if area else ""
            data['types'] = AssetType.objects.all()
            data['typeid'] = int(type) if type else ""
            data['depr'] = depr
            return render_to_response("assets/assets.html", data)
