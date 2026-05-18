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
        
        # Determine which forms are actually filled
        total_forms = int(post_data.get('form-TOTAL_FORMS', 0))
        filled_form_indices = []
        for i in range(total_forms):
            # A form is considered filled if at least the product name is typed or selected
            nama = post_data.get(f'form-{i}-nama_product', '').strip()
            qty = post_data.get(f'form-{i}-jumlah_produk', '').strip()
            price = post_data.get(f'form-{i}-harga_beli_satuan', '').strip()
            
            if nama or qty or price:
                filled_form_indices.append(i)
                
        # Rebuild clean POST data containing only filled forms to avoid empty rows triggering validation errors
        clean_post_data = post_data.copy()
        clean_post_data['form-TOTAL_FORMS'] = str(len(filled_form_indices))
        clean_post_data['form-INITIAL_FORMS'] = '0'
        clean_post_data['form-MIN_NUM_FORMS'] = '0'
        clean_post_data['form-MAX_NUM_FORMS'] = '1000'
        
        # Clear all original forms from clean_post_data
        for key in list(clean_post_data.keys()):
            if key.startswith('form-') and not any(key.startswith(f'form-{prefix}') for prefix in ['TOTAL_FORMS', 'INITIAL_FORMS', 'MIN_NUM_FORMS', 'MAX_NUM_FORMS']):
                del clean_post_data[key]
                
        # Copy file uploads dictionary to clean new files dict
        clean_files = request.FILES.copy()
        for key in list(request.FILES.keys()):
            if key.startswith('form-'):
                del clean_files[key]
                
        # Re-index filled forms sequentially starting from index 0
        for new_idx, old_idx in enumerate(filled_form_indices):
            # Inject current logged-in user profile ID
            clean_post_data[f'form-{new_idx}-user'] = str(request.user.profile.id)
            
            # Copy form fields and clean numerical values (commas)
            for field_name in ['nama_product', 'part_for_what', 'hsn_sac', 'jumlah_produk', 'vendor', 
                               'harga_beli_satuan', 'gst_percent', 'gst_amount', 'amt_incl_tax', 
                               'laba_persen', 'harga_jual_satuan', 'mrp']:
                old_key = f'form-{old_idx}-{field_name}'
                new_key = f'form-{new_idx}-{field_name}'
                if old_key in post_data:
                    val = post_data[old_key]
                    if field_name in ['harga_beli_satuan', 'harga_jual_satuan', 'mrp']:
                        val = val.replace(',', '').strip()
                    clean_post_data[new_key] = val
                    
            # Copy file/image attachment if present
            file_key = f'form-{old_idx}-image'
            if file_key in request.FILES:
                clean_files[f'form-{new_idx}-image'] = request.FILES[file_key]

        formset_post = DaftarBarangFormset(
            clean_post_data,
            clean_files,
            form_kwargs={'part_choices': part_choices},
        )
        if formset_post.is_valid():
            saved = 0
            for form in formset_post:
                if not form.cleaned_data.get('nama_product'):
                    continue
                jumlah = form.cleaned_data.get('jumlah_produk', 0) or 0
                
                # Retrieve price safely
                harga_beli_raw = form.data.get(form.add_prefix('harga_beli_satuan'), '0')
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
