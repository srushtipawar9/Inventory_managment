from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Stock, JCBPart, Vendor, VendorPartPrice
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

@admin.register(Stock)
class StockResources(ImportExportModelAdmin):
    list_display = ('id','name', 'price', 'created', 'updated')
    list_filter = ['name', 'price', ('created', DateRangeFilter)]

@admin.register(JCBPart)
class JCBPartAdmin(ImportExportModelAdmin):
    list_display = ('part_number', 'name', 'category', 'price', 'stock_quantity')
    list_filter = ('category', 'price')
    search_fields = ('part_number', 'name')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'contact_phone', 'updated_at')
    list_filter = ('city',)
    search_fields = ('name', 'city')


@admin.register(VendorPartPrice)
class VendorPartPriceAdmin(admin.ModelAdmin):
    list_display = ('part', 'vendor', 'price', 'updated_at')
    list_filter = ('vendor__city', 'part__category', 'vendor__name')
    search_fields = ('part__part_number', 'part__name', 'vendor__name', 'vendor__city')
