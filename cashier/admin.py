from django.contrib import admin
from cashier.models import DaftarBarang, DaftarTransaksi, ListProductTransaksi
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

admin.site.site_header = "JCB & Hydraulic Parts - Inventory Management"
admin.site.site_title = "JCB Parts Admin"
admin.site.index_title = "JCB Parts Inventory Dashboard"

class ListDaftarBarang(ImportExportModelAdmin):
    search_fields = ['nama_product']
    list_display = ('nomor', 'nama_product', 'jumlah_produk', 'harga_beli_satuan', 'laba_persen', 'harga_jual_satuan', 'subtotal_harga_jual', 'created')
    list_filter = ['user_id', 'nama_product', ('created', DateRangeFilter),]
    list_editable = ['jumlah_produk', 'harga_beli_satuan', 'laba_persen']

class ListProductTransaksiImport(admin.StackedInline):
    model = ListProductTransaksi

class TransactionResources(ImportExportModelAdmin):
    search_fields = ['total']
    list_display = ('nomor', 'produk_jumlah', 'total', 'created')
    list_filter = ['user_id', 'total', ('created', DateRangeFilter),]

class ListProductTransaksiAdmin(admin.ModelAdmin):
    list_display = ('transaksi_id', 'nama_barang', 'quantity', 'subtotal', 'created')
    list_filter = ['nama_barang', ('created', DateRangeFilter)]

admin.site.register(DaftarBarang, ListDaftarBarang)
admin.site.register(DaftarTransaksi, TransactionResources)
admin.site.register(ListProductTransaksi, ListProductTransaksiAdmin)
