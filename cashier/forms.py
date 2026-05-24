from decimal import Decimal

from django import forms
from cashier.models import DaftarBarang, DaftarTransaksi, ListProductTransaksi


class DaftarBarangForm(forms.ModelForm):
    class Meta:
        model = DaftarBarang
        fields = [
            'user',
            'nama_product',
            'image',
            'part_for_what',
            'hsn_sac',
            'jumlah_produk',
            'vendor',
            'company',
            'harga_beli_satuan',
            'gst_percent',
            'gst_amount',
            'amt_incl_tax',
            'laba_persen',
            'harga_jual_satuan',
            'mrp',
            'status',
        ]
        widgets = {
            'nama_product': forms.Select(attrs={'class': 'form-control part-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'part_for_what': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. / For What'}),

            'hsn_sac': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HSN / SAC'}),
            'jumlah_produk': forms.NumberInput(attrs={'class': 'form-control calc-field', 'placeholder': 'Qty', 'min': '1'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor', 'list': 'vendor-list'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company (e.g. JCB, CAT)', 'list': 'company-list'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'harga_beli_satuan': forms.TextInput(attrs={'class': 'form-control calc-field', 'placeholder': 'Purchase'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control calc-field', 'placeholder': 'GST %', 'step': '0.01', 'min': '0'}),
            'gst_amount': forms.TextInput(attrs={'class': 'form-control calc-field', 'placeholder': 'GST Amt', 'readonly': 'readonly'}),
            'amt_incl_tax': forms.TextInput(attrs={'class': 'form-control calc-field', 'placeholder': 'Incl Tax', 'readonly': 'readonly'}),
            'laba_persen': forms.NumberInput(attrs={'class': 'form-control calc-field', 'placeholder': '%', 'min': '0'}),
            'harga_jual_satuan': forms.TextInput(attrs={'class': 'form-control calc-field', 'placeholder': 'Sales'}),
            'mrp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MRP'}),
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        part_choices = kwargs.pop('part_choices', None)
        super().__init__(*args, **kwargs)
        self.fields['nama_product'].required = False
        self.fields['part_for_what'].required = False
        self.fields['hsn_sac'].required = False
        self.fields['vendor'].required = False
        self.fields['company'].required = False
        self.fields['status'].required = False
        self.fields['gst_percent'].required = False
        self.fields['gst_amount'].required = False
        self.fields['amt_incl_tax'].required = False
        self.fields['mrp'].required = False
        self.fields['harga_jual_satuan'].required = False
        self.fields['image'].required = False

        if part_choices is not None:
            self.fields['nama_product'] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control part-select', 'list': 'part-list', 'placeholder': 'Item Name'}),
                required=False,
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


"Form Daftar Transaksi"
class DaftarTransaksiForm(forms.ModelForm):
    class Meta:
        model = DaftarTransaksi
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class ListProductTransaksiForm(forms.ModelForm):
    class Meta:
        model = ListProductTransaksi
        fields = '__all__'


class TransaksiProductListForm(forms.Form):
    nama_barang = forms.CharField(max_length=100)
    quantity = forms.IntegerField(initial=0)
    user = forms.IntegerField()

    def save(self, transaksi):
        quantity = self.cleaned_data['quantity']
        produk = DaftarBarang.objects.get(nomor=self.cleaned_data['nama_barang'])

        if produk.jumlah_produk >= int(quantity):
            produk.jumlah_produk = produk.jumlah_produk - int(quantity)
            if produk.jumlah_produk == 0:
                produk.delete()
            else:
                produk.subtotal_harga_beli = produk.jumlah_produk * produk.harga_beli_satuan
                laba_persen = produk.laba_persen * produk.subtotal_harga_beli / 100
                produk.subtotal_harga_jual = laba_persen + produk.subtotal_harga_beli
                produk.save()
        else:
            return False

        subtotal_produk = produk.harga_jual_satuan * int(quantity)
        produk_transaksi = ListProductTransaksi.objects.create(
            transaksi_id=transaksi,
            nama_barang=produk.nama_product,
            subtotal=subtotal_produk,
            quantity=quantity,
        )
        produk_transaksi.save()
        return produk_transaksi
