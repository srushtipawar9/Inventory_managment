from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Stock, JCBPart
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

@admin.register(Stock)
class StockResources(ImportExportModelAdmin):
    list_display = ('id','name', 'price', 'created', 'updated')
    list_filter = ['name', 'price', ('created', DateRangeFilter)]

@admin.register(JCBPart)
class JCBPartAdmin(ImportExportModelAdmin):
    list_display = ('part_number', 'name', 'category', 'price', 'stock_quantity')
    list_filter = ('category', 'price')
    search_fields = ('part_number', 'name')
