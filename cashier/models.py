from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.models import Profile
from data.models import Stock
from django.utils.timezone import now
from cloudinary.models import CloudinaryField

"Stock Input"
class DaftarBarang(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nomor = models.AutoField(primary_key=True)
    # nama_product = models.ForeignKey(Stock, on_delete=models.CASCADE)
    nama_product = models.CharField(max_length=200, blank=False, null=False)
    image = models.ImageField(upload_to='jcb_parts/', null=True, blank=True)
    part_for_what = models.CharField(max_length=100, blank=True, default='')
    hsn_sac = models.CharField(max_length=30, blank=True, default='')
    jumlah_produk = models.IntegerField()

    unit_produk = models.IntegerField(blank=True, null=True)
    vendor = models.CharField(max_length=120, blank=True, default='')
    company = models.CharField(max_length=100, blank=True, default='', verbose_name='Company / Manufacturer')

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Hidden', 'Hidden'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
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

    def save(self, *args, **kwargs):
        from decimal import Decimal
        qty = Decimal(self.jumlah_produk or 0)
        purchase = Decimal(self.harga_beli_satuan or 0)
        gst_pct = Decimal(self.gst_percent or 0)
        profit_pct = Decimal(self.laba_persen or 10)

        self.product_price = purchase
        base = purchase * qty

        # Always recalculate so edits are properly saved (bug fix: was using `if not`)
        self.gst_amount = (base * gst_pct / Decimal('100')).quantize(Decimal('0.01'))
        self.amt_incl_tax = (base + self.gst_amount).quantize(Decimal('0.01'))

        self.subtotal_harga_beli = base.quantize(Decimal('0.01'))
        # Always recalculate sell price from current purchase price + profit
        self.harga_jual_satuan = (
            purchase + (purchase * profit_pct / Decimal('100'))
        ).quantize(Decimal('0.01'))

        sell_unit = Decimal(self.harga_jual_satuan)
        self.marp = Decimal(self.mrp or 0)
        self.marp_sell_val = sell_unit
        self.marp_last_amount = Decimal(self.amt_incl_tax)
        laba = (Decimal(profit_pct) * self.subtotal_harga_beli) / Decimal('100')
        self.subtotal_harga_jual = (laba + self.subtotal_harga_beli).quantize(Decimal('0.01'))
        self.marp_last_amount_total = self.subtotal_harga_jual

        super().save(*args, **kwargs)


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


# ── Estimate Slip Models ────────────────────────────────────────────────────

class EstimateSlip(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, null=True, blank=True)
    estimate_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=now, editable=False)

    class Meta:
        verbose_name = 'Estimate Slip'
        verbose_name_plural = 'Estimate Slips'
        ordering = ['-created_at']

    def __str__(self):
        return f"Estimate #{self.estimate_no} – {self.customer_name}"


class EstimateSlipItem(models.Model):
    estimate = models.ForeignKey(EstimateSlip, on_delete=models.CASCADE, related_name='items')
    particulars = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        self.amount = Decimal(str(self.quantity)) * Decimal(str(self.rate))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.particulars


# ── Financial Insight Report Header ─────────────────────────────────────────

class FinancialInsightReport(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, default='')
    mobile_number = models.CharField(max_length=15, blank=True, default='')
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)

    class Meta:
        verbose_name = 'Financial Insight Report'
        verbose_name_plural = 'Financial Insight Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} – {self.date}"

