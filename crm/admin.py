from django.contrib import admin
from .models import Customer, PaymentReminder
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    list_display = ('name', 'phone', 'email', 'outstanding_balance', 'created_at', 'updated_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('outstanding_balance', ('created_at', DateRangeFilter))
    list_editable = ('phone', 'outstanding_balance')

@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'sent_at')
    list_filter = ('status', ('sent_at', DateRangeFilter))
    search_fields = ('customer__name',)
