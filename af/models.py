#! /usr/bin/env python
# -*- coding: utf-8 -*-

from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Sum


class Area(models.Model):
    name = models.CharField(max_length=100)
    responsible = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return u"{0}".format(self.name)

    class Meta:
        verbose_name = u'Area'
        verbose_name_plural = u'Areas'
        db_table = 'assets_areas'
        unique_together = ('name', )
        ordering = ('name', )

    def assets_quantity(self):
        return self.asset_set.count()

    def assets_values(self):
        if self.assets_quantity():
            return self.asset_set.aggregate(Sum('current_value'))['current_value__sum']
        return 0

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super(Area, self).save(force_insert, force_update, using)


class AssetType(models.Model):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)

    def __str__(self):
        return u"{0}".format(self.name)

    class Meta:
        verbose_name = u'Type'
        verbose_name_plural = u'Types'
        db_table = 'assets_types'
        unique_together = ('name', )
        ordering = ('name', )

    def assets_quantity(self):
        return self.asset_set.count()

    def assets_values(self):
        if self.assets_quantity():
            return self.asset_set.aggregate(Sum('current_value'))['current_value__sum']
        return 0

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super(AssetType, self).save(force_insert, force_update, using)


class Asset(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    type = models.ForeignKey(AssetType)
    area = models.ForeignKey(Area)
    entry_date = models.DateField(auto_now_add=True, blank=True, null=True)
    initial_value = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    current_value = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    is_depreciable = models.BooleanField(default=True)
    foto = models.FileField(upload_to='fotos/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return u"{0} - {1}, Type: {2} - (Initial: ${3}, Current: ${4})".format(self.code,
                                                                               self.description,
                                                                               self.type,
                                                                               self.initial_value,
                                                                               self.current_value)

    class Meta:
        verbose_name = u'Asset'
        verbose_name_plural = u'Assets'
        db_table = 'assets_assets'
        unique_together = ('code', )
        ordering = ('entry_date', 'code')

    def simple_name(self):
        return u"{0} - {1} ({2})".format(self.code, self.description, self.type)

    def value_to_depreciate(self):
        if self.current_value and self.type.rate:
            return (self.current_value * self.type.rate) / Decimal(100.0)
        return 0

    def depreciated_value(self):
        if self.assetdepreciationdetail_set.exists():
            return sum([x.depreciated_value for x in self.assetdepreciationdetail_set.all()])
        return 0

    def download_foto(self):
        return self.foto.url

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super(Asset, self).save(force_insert, force_update, using)


class AssetDepreciationTotal(models.Model):
    date = models.DateField(auto_now_add=True)
    total_before = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    total_depreciated = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)

    def __str__(self):
        return u"Depr Total: ${0}, Date: {1} (Before Total: ${2})".format(self.total_depreciated,
                                                                          self.date.strftime('%d-%m-%Y'),
                                                                          self.total_before)

    class Meta:
        verbose_name = u'Depreciation Total'
        verbose_name_plural = u'Depreciation Totals'
        db_table = 'assets_depreciationtotal'
        unique_together = ('date', )
        ordering = ('date', )


class AssetDepreciationDetail(models.Model):
    depreciation_total = models.ForeignKey(AssetDepreciationTotal)
    asset = models.ForeignKey(Asset)
    before_value = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    rate = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    depreciated_value = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    area = models.ForeignKey(Area, blank=True, null=True)

    def __str__(self):
        return "Depr: {0}, Rate: {1} (ValueDepr: ${2})".format(self.asset, self.rate, self.depreciated_value)

    class Meta:
        verbose_name = u'Depreciation Detail'
        verbose_name_plural = u'Depreciations Details'
        db_table = 'assets_depreciationdetail'
        unique_together = ('depreciation_total', 'asset')
        ordering = ('area', 'asset')
