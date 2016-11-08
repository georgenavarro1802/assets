from django.contrib import admin

from af.models import Area, AssetType, Asset, AssetDepreciationTotal, AssetDepreciationDetail


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'responsible')
    search_fields = ('name', 'responsible')

admin.site.register(Area, AreaAdmin)


class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate')
    search_fields = ('name',)
    list_filter = ('rate',)

admin.site.register(AssetType, AssetTypeAdmin)


class AssetAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'type', 'area', 'entry_date', 'initial_value', 'current_value',
                    'is_depreciable', 'foto')
    search_fields = ('code', 'description', 'descripcion')
    list_filter = ('type', 'area')

admin.site.register(Asset, AssetAdmin)


class AssetDepreciationTotalAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_before', 'total_depreciated')

admin.site.register(AssetDepreciationTotal, AssetDepreciationTotalAdmin)


class AssetDepreciationDetailAdmin(admin.ModelAdmin):
    list_display = ('depreciation_total', 'asset', 'before_value', 'rate', 'depreciated_value', 'area')
    search_fields = ('asset__code', 'asset_description')
    list_filter = ('rate', 'area')

admin.site.register(AssetDepreciationDetail, AssetDepreciationDetailAdmin)
