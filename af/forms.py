#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from decimal import Decimal
from django import forms
from af.models import AssetType, Area


class ExtFileField(forms.FileField):
    """
    * max_upload_size - a number indicating the maximum file size allowed for upload.
            500Kb - 524288
            1MB - 1048576
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    t = ExtFileField(ext_whitelist=(".pdf", ".txt"), max_upload_size=)
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()

            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de fichero o tamanno no permitido!")


class AssetsForm(forms.Form):
    code = forms.CharField(label=u'Code', max_length=10,
                           widget=forms.TextInput(attrs={'class': 'form-control input-25'}))
    description = forms.CharField(label=u'Description', max_length=200,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ModelChoiceField(AssetType.objects, label=u"Type",
                                  widget=forms.Select(attrs={'class': 'form-control input-50'}))
    area = forms.ModelChoiceField(Area.objects, label=u"Area",
                                  widget=forms.Select(attrs={'class': 'form-control input-50'}))
    entry_date = forms.DateField(label=u'Entry date', input_formats=['%d-%m-%Y'],
                                 widget=forms.DateTimeInput(format='%d-%m-%Y',
                                                            attrs={'class': 'form-control input-25'}))
    initial_value = forms.DecimalField(initial=Decimal('0.00'), max_digits=11, decimal_places=2, label=u'iInitial Val',
                                       widget=forms.TextInput(attrs={'class': 'form-control input-25'}))
    current_value = forms.DecimalField(initial=Decimal('0.00'), max_digits=11, decimal_places=2, label=u'Current Val',
                                       widget=forms.TextInput(attrs={'class': 'form-control input-25'}))
    is_depreciable = forms.BooleanField(initial=True, label='Depreciable?', required=False)
    foto = ExtFileField(label='Photo', required=False,
                        help_text=u'Maximum size alloweb 2 mb in formats like: jpeg, jpg, gif, png, bmp',
                        ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp"), max_upload_size=2097152)
