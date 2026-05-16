from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.models import Profile
from data.models import Stock
from django.utils.timezone import now

"Stock Input"
class DaftarBarang(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nomor = models.AutoField(primary_key=True)
    # nama_product = models.ForeignKey(Stock, on_delete=models.CASCADE)
    nama_product = models.CharField(max_length=200, blank=False, null=False)
    image = models.ImageField(upload_to='inventory_images/', blank=True, null=True)
    part_for_what = models.CharField(max_length=100, blank=True, default='')
    hsn_sac = models.CharField(max_length=30, blank=True, default='')
    jumlah_produk = models.IntegerField()

    unit_produk = models.IntegerField(blank=True, null=True)
    vendor = models.CharField(max_length=120, blank=True, default='')
    harga_beli_satuan = models.DecimalField(max_digits=14, decimal_places=2)
    product_price = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    gst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    amt_incl_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    subtotal_harga_beli = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    laba_persen = models.IntegerField(default=10)
    harga_jual_satuan = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    mrp = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    marp = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    marp_sell_val = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    marp_last_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    marp_last_amount_total = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    subtotal_harga_jual = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    created = models.DateTimeField(default=now , editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "JCB Part Inventory"
        verbose_name_plural = "JCB Parts Inventory"

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.nama_product


"Daftar Transaksi"
class DaftarTransaksi(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nomor = models.AutoField(primary_key=True)
    produk_jumlah = models.PositiveIntegerField(blank=True, null=True)
    total = models.DecimalField(max_digits=9, decimal_places=2, blank=True, default=0)

    created = models.DateTimeField(default=now, editable=False)
    updated = models.DateTimeField(default=now, editable=False)

    class Meta:
        verbose_name = "Sales Transaction"
        verbose_name_plural = "Sales Transactions"

    def publish(self):

        self.published_date = timezone.now()

    def __str__(self):
        return str(self.nomor)


class ListProductTransaksi(models.Model):
    transaksi_id = models.ForeignKey(DaftarTransaksi, on_delete=models.CASCADE)
    nama_barang = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.PositiveIntegerField(blank=True, null=True, default=0)
    subtotal = models.PositiveIntegerField(blank=True, null=True)
    created = models.DateTimeField(default=now, editable=False)

    class Meta:
        verbose_name = "Sales Product List"
        verbose_name_plural = "Sales Product Lists"

    def publish(self):

        self.published_date = timezone.now()

    def __str__(self):
        return str(self.nama_barang)
