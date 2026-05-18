from django.shortcuts import render, redirect, reverse, get_object_or_404
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import (
    DaftarBarang,
    DaftarTransaksi,
    ListProductTransaksi,

)
from accounts.models import Profile
from cashier.forms import (
    DaftarBarangForm,
    TransaksiProductListForm,
    ListProductTransaksiForm,
    DaftarTransaksiForm,
)
from django.utils.timezone import datetime
from data.models import JCBPart, Vendor


def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

@login_required()
def HomeIndex(request):
    today = datetime.today()
    data = DaftarBarang.objects.filter(user_id = request.user.id)
    data_pendapatan = DaftarTransaksi.objects.filter(created__day=today.day,user_id=request.user.id)
    pendapatan_hari_ini = 0
    if data_pendapatan is not None :
        for pendapatan in data_pendapatan:
            pendapatan_hari_ini += Decimal(pendapatan.total)
    #         # raise ValueError(data_pendapatan)
    context = {
        'data': data,
        'data_pendapatan': pendapatan_hari_ini
    }
    return render(request, 'cashier/home.html', context)

def _part_choices(stocks, prefill=''):
    choices = [('', '-- Select Item --')]
    for stock in stocks:
        label = f"{stock.part_number} - {stock.name}"
        choices.append((label, label))
    return choices


@login_required()
def InputStock(request):
    DaftarBarangFormset = formset_factory(DaftarBarangForm, extra=1)
    stocks = JCBPart.objects.all().order_by('category', 'name')
    prefill = request.GET.get('prefill', '')
    part_choices = _part_choices(stocks, prefill)
    vendor_names = list(
        Vendor.objects.order_by('city', 'name').values_list('name', flat=True).distinct()
    )
    if request.method == 'POST':
        post_data = request.POST.copy()
        
        # Ensure user field is filled for all forms in the post data to prevent validation errors
        total_forms = int(post_data.get('form-TOTAL_FORMS', 0))
        for i in range(total_forms):
            post_data[f'form-{i}-user'] = str(request.user.profile.id)
            
        for key in post_data.keys():
            if any(suffix in key for suffix in ['-harga_beli_satuan', '-harga_jual_satuan', '-mrp']):
                post_data[key] = post_data[key].replace(',', '').strip()

        formset_post = DaftarBarangFormset(
            post_data,
            request.FILES,
            form_kwargs={'part_choices': part_choices},
        )
        if formset_post.is_valid():
            saved = 0
            for form in formset_post:
                if not form.cleaned_data.get('nama_product'):
                    continue
                jumlah = form.cleaned_data.get('jumlah_produk', 0) or 0
                
                # Clean purchase price comma for checking
                harga_beli_raw = form.data.get(form.add_prefix(form.prefix) + '-harga_beli_satuan', '0')
                try:
                    harga = Decimal(str(harga_beli_raw).replace(',', '').strip())
                except:
                    harga = Decimal('0')

                if jumlah < 1 or harga < 1:
                    messages.warning(
                        request,
                        f'Qty and Purchase Price required for {form.cleaned_data.get("nama_product")}',
                    )
                    continue
                form.save()
                saved += 1
            if saved:
                messages.success(request, f'Inventory saved successfully! ({saved} item(s))')
                return HttpResponseRedirect('/input/')
            messages.warning(request, 'No valid rows to save. Please fill Item Name, Qty and Purchase Price.')
        else:
            messages.warning(request, 'Please correct the highlighted fields and try again.')

        context = {
            'stocks': stocks,
            'forms': formset_post,
            'request_user': request.user.profile.id,
            'prefill': prefill,
            'vendor_names': vendor_names,
        }
        return render(request, 'cashier/input_data.html', context)

    formset = DaftarBarangFormset(
        initial=[{'user': request.user.profile.id}],
        form_kwargs={'part_choices': part_choices}
    )
    context = {
        'stocks': stocks,
        'forms': formset,
        'request_user': request.user.profile.id,
        'prefill': prefill,
        'vendor_names': vendor_names,
    }
    return render(request, 'cashier/input_data.html', context)
@login_required()
def TotalStock(request):
    data = DaftarBarang.objects.filter(user_id=request.user.profile.id)
    context = {
        'data':data
    }
    return render(request, 'cashier/stock.html', context)


@login_required()
def EditStock(request, pk):
    item = get_object_or_404(DaftarBarang, nomor=pk, user_id=request.user.profile.id)
    stocks = JCBPart.objects.all().order_by('category', 'name')
    part_choices = _part_choices(stocks)
    vendor_names = list(
        Vendor.objects.order_by('city', 'name').values_list('name', flat=True).distinct()
    )
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        for key in ['harga_beli_satuan', 'harga_jual_satuan', 'mrp']:
            if key in post_data:
                post_data[key] = post_data[key].replace(',', '').strip()
        form = DaftarBarangForm(post_data, request.FILES, instance=item, part_choices=part_choices)
        if form.is_valid():
            form.save()
            messages.success(request, f"Inventory item '{item.nama_product}' updated successfully!")
            return redirect('TotalStock')
        else:
            messages.warning(request, "Please correct the errors in the form.")
    else:
        form = DaftarBarangForm(instance=item, part_choices=part_choices)
        
    context = {
        'form': form,
        'item': item,
        'stocks': stocks,
        'vendor_names': vendor_names,
    }
    return render(request, 'cashier/edit_stock.html', context)


@login_required()
def DeleteStock(request, pk):
    item = get_object_or_404(DaftarBarang, nomor=pk, user_id=request.user.profile.id)
    name = item.nama_product
    item.delete()
    messages.success(request, f"Inventory item '{name}' deleted successfully!")
    return redirect('TotalStock')


@login_required()
def Cart(request):
    TransaksiListProdukFormset = formset_factory(TransaksiProductListForm , extra=1)
    formset = TransaksiListProdukFormset()
    data = DaftarBarang.objects.filter(user_id=request.user.id)

    if request.method == 'POST':
        formset_post = TransaksiListProdukFormset(request.POST)
        if formset_post.is_valid():
            total_harga_transaksi = 0
            total_jumlah_transaksi = 0
            transaksi = DaftarTransaksi.objects.create(user_id=request.user.id)
            transaksi.save()
            for form in formset_post:
                #print(form.cleaned_data)
                "if quantity == 0"
                if form.cleaned_data['quantity'] < 1:
                    messages.warning(request, 'Jumlah barang yang dibeli tidak boleh kosong!')
                    return redirect('/cart/')
                output = form.save(transaksi)
                "False == Transaksi Gagal"
                if(output == False):
                    messages.warning(request, 'Barang melebihi batas stock!')
                    return redirect('/cart/')

                "Hitung Total Harga Transaksi"
                total_harga_transaksi += output.quantity
                "Hitung Total Jumlah Transaksi"
                total_jumlah_transaksi += output.subtotal
            "Update Total Ke DaftarTransaksi"
            transaksi.total = total_jumlah_transaksi
            transaksi.produk_jumlah = total_harga_transaksi
            transaksi.save()
            "True == Transaksi Sukses"
            messages.success(request, 'Transaksi Berhasil!')
            return HttpResponseRedirect('/struck/'+str(transaksi.nomor)+'/')
        else:
            messages.warning(request, 'Data yang dibeli tidak boleh kosong!')
            return redirect('/cart/')
    else:
        context = {
            'data_barang': data,
            'forms': formset,
            'request_user': request.user.id,
        }
        return render(request, 'cashier/cart.html', context)

@login_required()
def StruckPembelian(request, pk):
    dataStruck = DaftarTransaksi.objects.get(nomor=pk)
    dataStruckListProduk = ListProductTransaksi.objects.filter(transaksi_id=dataStruck.nomor)
    dataUser = Profile.objects.get(id=dataStruck.user_id)
    context = {
        'dataStruck': dataStruck,
        'dataStruckListProduk': dataStruckListProduk,
        'dataUser': dataUser
    }
    return render(request, 'cashier/struck.html', context)

@login_required()
def DaftarPembelian(request):
    data = DaftarTransaksi.objects.filter(user_id=request.user.id)
    context = {
        'data': data,
    }
    return render(request, 'cashier/purchased.html', context)


@login_required()
def ReportView(request):
    if request.is_ajax():
        endDate = None
        startDate = request.GET.get('startDate')
        if request.GET.get('endDate') == '' or request.GET.get('endDate') is None :
            endDateConverter = datetime.today()
        else:
            endDate = request.GET.get('endDate')
            endDateConverter = datetime.strptime(endDate, "%Y-%m-%d").date()
        startDateConverter = datetime.strptime(startDate, "%Y-%m-%d").date()
        from_user = DaftarTransaksi.objects.filter(user_id=request.user.id,
                                                   created__date__gte=startDateConverter,
                                                   created__date__lte = endDateConverter)
        daftar_barang = ListProductTransaksi.objects.filter(transaksi_id__in=from_user)
        return render(request, 'cashier/report_details.html', {'daftar_barang': daftar_barang, 'num': startDateConverter})

    from_user = DaftarTransaksi.objects.filter(user_id=request.user.id)
    daftar_barang = ListProductTransaksi.objects.filter(transaksi_id__in=from_user)


    context = {
        'daftar_barang': daftar_barang,
        'from_user': from_user,

    }
    return render(request, 'cashier/report.html', context)
