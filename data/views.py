from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
import requests
from .resources import StockResource

from tablib import Dataset
from .models import JCBPart, Stock, VendorPartPrice, Vendor
from cashier.models import DaftarBarang
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def GlobalSearch(request):
    query = request.GET.get('q', '').strip()
    
    context = {
        'categorized_parts': {},
        'stocks': [],
        'inventory_results': [],
        'amazon_results': [],
        'extra_parts': [],
        'jcb_products': [],
        'query': query,
        'has_parts': False
    }
    
    if query:
        # Search in JCBPart
        parts_list = JCBPart.objects.filter(
            Q(name__icontains=query) | Q(part_number__icontains=query) | Q(description__icontains=query)
        ).order_by('category')
        
        # Group parts by category
        categorized_parts = {}
        for part in parts_list:
            cat_name = part.get_category_display()
            if cat_name not in categorized_parts:
                categorized_parts[cat_name] = []
            categorized_parts[cat_name].append(part)
            
        # Search in Stock (Legacy)
        stocks = Stock.objects.filter(name__icontains=query)
        
        # Search in Inventory (DaftarBarang)
        inventory_results = DaftarBarang.objects.filter(
            Q(nama_product__icontains=query) | Q(vendor__icontains=query) | Q(hsn_sac__icontains=query)
        ).order_by('-created')

        # --- Amazon Marketplace Integration ---
        amazon_results = []
        try:
            headers = {
                "x-rapidapi-key": "a536bdbeafmshfc70cd8bb5336c9p146880jsnc8af7367cb7a",
                "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
            }
            url = "https://real-time-amazon-data.p.rapidapi.com/search"
            querystring = {"query": query, "page": "1", "country": "IN", "sort_by": "RELEVANCE"}
            response = requests.get(url, headers=headers, params=querystring, timeout=5)
            if response.status_code == 200:
                amazon_results = response.json().get('data', {}).get('products', [])[:8]
        except Exception as e:
            print(f"Amazon API Error: {e}")
        
        context.update({
            'categorized_parts': categorized_parts,
            'stocks': stocks,
            'inventory_results': inventory_results,
            'amazon_results': amazon_results,
            'has_parts': len(parts_list) > 0 or inventory_results.exists()
        })
        
    return render(request, 'data/search_results.html', context)



def PartDetail(request, part_id):
    part = get_object_or_404(JCBPart, id=part_id)
    if request.method == 'POST' and request.FILES.get('image'):
        if part.image_360_base:
            part.image_360_base.delete(save=False)
        part.image_360_base = request.FILES.get('image')
        part.save()
        messages.success(request, f"Product image for part '{part.part_number}' uploaded successfully!")
        return redirect('PartDetail', part_id=part.id)
    return render(request, 'data/part_detail.html', {'part': part})

def StockUpload(request):
    if request.method == 'POST':
        from .resources import JCBPartResource
        from django.contrib import messages
        jcb_resource = JCBPartResource()
        dataset = Dataset()
        new_file = request.FILES.get('file')

        if not new_file:
            messages.warning(request, 'Please select a file to upload.')
            return render(request, 'data/upload.html')

        try:
            # Detect format from extension
            file_ext = new_file.name.split('.')[-1].lower()
            new_file.seek(0)
            
            if file_ext == 'csv':
                imported_data = dataset.load(new_file.read().decode('utf-8'), format='csv')
            elif file_ext in ['xls', 'xlsx']:
                imported_data = dataset.load(new_file.read(), format=file_ext)
            else:
                messages.warning(request, 'Unsupported file format. Please upload CSV, XLS, or XLSX.')
                return render(request, 'data/upload.html')

            # Dry run first
            result = jcb_resource.import_data(dataset, dry_run=True)

            if not result.has_errors():
                jcb_resource.import_data(dataset, dry_run=False)
                messages.success(request, f'Successfully imported {result.total_rows} JCB parts!')
            else:
                messages.warning(request, 'Error in import. Please check your file format.')
        except Exception as e:
            messages.warning(request, f'Upload failed: {str(e)}')

    return render(request, 'data/upload.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def ImportAmazonPart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Use ASIN to create a unique part number
            part_no = f"AMZ-{data.get('asin', 'TEMP')}"
            
            # Check if part already exists
            existing = JCBPart.objects.filter(part_number=part_no).first()
            if existing:
                return JsonResponse({'success': True, 'already_exists': True, 'part_id': existing.id})

            # Create a new JCBPart from Amazon data
            price_str = data.get('price', '0').replace('$', '').replace('₹', '').replace(',', '').strip()
            try:
                price = float(price_str)
            except:
                price = 0.0
                
            new_part = JCBPart.objects.create(
                part_number=part_no,
                name=data.get('title')[:200],
                description=f"Imported from Amazon: {data.get('url')}",
                price=price,
                stock_quantity=10,
                category='OTHER'
            )
            
            # Download image locally with robust logic
            image_url = data.get('image')
            if image_url:
                try:
                    import requests
                    from django.core.files.base import ContentFile
                    
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Create a filename from ASIN
                        img_filename = f"{data.get('asin', 'part')}.jpg"
                        new_part.image_360_base.save(img_filename, ContentFile(img_response.content), save=False)
                    else:
                        new_part.image_360_base = image_url
                except Exception as e:
                    print(f"Fallback to external URL for JCBPart: {e}")
                    new_part.image_360_base = image_url

            new_part.save()
            
            return JsonResponse({'success': True, 'already_exists': False, 'part_id': new_part.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def MasterCatalog(request):
    parts = JCBPart.objects.all().order_by('category', 'name')
    return render(request, 'data/master_catalog.html', {'parts': parts})


@login_required
def VendorComparison(request):
    """
    City-wise vendor price comparison — green = cheapest, red = costliest.
    Data is fully pre-computed so the template needs no custom tags.
    """
    category = (request.GET.get("category") or "ALL").upper()
    valid_cats = ["HYDRAULICS", "POWERTRAIN", "GET", "FILTERS",
                  "ELECTRICAL", "CHASSIS", "OTHER", "ALL"]
    if category not in valid_cats:
        category = "ALL"

    prices_qs = (
        VendorPartPrice.objects.select_related("vendor", "part")
        .order_by("part__category", "part__name", "vendor__city", "vendor__name")
    )
    if category != "ALL":
        prices_qs = prices_qs.filter(part__category=category)

    # Force evaluation once so we can iterate multiple times
    prices_list = list(prices_qs)

    # Collect all unique cities (sorted)
    all_cities = sorted(set(vp.vendor.city for vp in prices_list))

    # Build per-part dict: part_id -> {part, city_prices{city->{price,vendor_name}}}
    parts_map = {}
    for vp in prices_list:
        p = vp.part
        if p.id not in parts_map:
            parts_map[p.id] = {"part": p, "city_prices": {}}
        city = vp.vendor.city
        existing = parts_map[p.id]["city_prices"].get(city)
        if existing is None or vp.price < existing["price"]:
            parts_map[p.id]["city_prices"][city] = {
                "price": vp.price,
                "vendor_name": vp.vendor.name,
            }

    # Build final rows with pre-computed cells (one per city) + color_class
    parts_entries = []
    for entry in parts_map.values():
        city_prices = entry["city_prices"]
        prices = [v["price"] for v in city_prices.values()]
        min_p = min(prices) if prices else None
        max_p = max(prices) if prices else None

        cells = []
        for city in all_cities:
            info = city_prices.get(city)
            if info is None:
                cells.append(None)  # no data for this city
            else:
                if min_p == max_p:
                    css = "cell-cheapest"          # only one price → neutral green
                elif info["price"] == min_p:
                    css = "cell-cheapest"
                elif info["price"] == max_p:
                    css = "cell-costliest"
                else:
                    css = "cell-mid"
                cells.append({
                    "price": info["price"],
                    "vendor_name": info["vendor_name"],
                    "css": css,
                })

        parts_entries.append({
            "part": entry["part"],
            "cells": cells,
            "min_price": min_p,
            "max_price": max_p,
        })

    category_choices = [
        ("ALL", "All Parts"), ("HYDRAULICS", "Hydraulics"),
        ("POWERTRAIN", "Powertrain"), ("GET", "Ground Engaging Tools"),
        ("FILTERS", "Filters"), ("ELECTRICAL", "Electrical"),
        ("CHASSIS", "Chassis"), ("OTHER", "Other"),
    ]

    context = {
        "category": category,
        "all_cities": all_cities,
        "parts_entries": parts_entries,
        "category_choices": category_choices,
    }
    return render(request, "data/vendors.html", context)

@login_required
def VendorPriceAdd(request):
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        part_id = request.POST.get('part_id')
        price = request.POST.get('price')
        notes = request.POST.get('notes', '')

        if vendor_id and part_id and price:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            part = get_object_or_404(JCBPart, id=part_id)
            
            # Update or create the price entry
            price_entry, created = VendorPartPrice.objects.update_or_create(
                vendor=vendor,
                part=part,
                defaults={'price': price, 'notes': notes}
            )
            
            if created:
                messages.success(request, f'Price added successfully for {part.part_number} at {vendor.name}')
            else:
                messages.success(request, f'Price updated successfully for {part.part_number} at {vendor.name}')
                
            return redirect('VendorComparison')
        else:
            messages.error(request, 'Please fill in all required fields.')

    context = {
        'vendors': Vendor.objects.all().order_by('name'),
        'parts': JCBPart.objects.all().order_by('part_number', 'name'),
        'recent_prices': VendorPartPrice.objects.select_related('vendor', 'part').order_by('-updated_at')[:5]
    }
    return render(request, 'data/vendor_price_add.html', context)



@login_required
def RemovePartImage(request, part_id):
    part = get_object_or_404(JCBPart, id=part_id)
    if part.image_360_base:
        # Delete the actual file if you want, or just clear the field
        part.image_360_base.delete(save=False)
        part.image_360_base = None
        part.save()
        messages.success(request, f"Image removed for {part.part_number}")
    return redirect(request.META.get('HTTP_REFERER', '/data/search/'))

@login_required
def QuickAddProduct(request):
    if request.method == 'POST':
        part_number = request.POST.get('part_number')
        name = request.POST.get('name')
        price = request.POST.get('price', 0)
        category = request.POST.get('category', 'OTHER')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        try:
            new_part, created = JCBPart.objects.update_or_create(
                part_number=part_number,
                defaults={
                    'name': name,
                    'price': price,
                    'category': category,
                    'description': description,
                    'stock_quantity': 0
                }
            )
            if image:
                if new_part.image_360_base:
                    new_part.image_360_base.delete(save=False)
                new_part.image_360_base = image
                new_part.save()
            
            if created:
                messages.success(request, f"Product '{name}' added successfully to catalog!")
            else:
                messages.success(request, f"Product '{name}' already existed and has been updated in catalog!")
        except Exception as e:
            messages.error(request, f"Error processing product: {str(e)}")
            
    return redirect(request.META.get('HTTP_REFERER', '/data/search/'))


@login_required
def SaveAIInventory(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            image_url = data.get('image_url')
            name = data.get('name')
            
            # Robust type conversion to prevent ValueErrors when numeric inputs are blank or invalid
            try:
                qty = int(data.get('qty') or 1)
            except:
                qty = 1
                
            try:
                purchase_price = float(str(data.get('purchase_price') or 0).replace(',', '').strip())
            except:
                purchase_price = 0.0
                
            try:
                profit_margin = int(data.get('profit_margin') or 10)
            except:
                profit_margin = 10
                
            try:
                gst_percent = float(str(data.get('gst_percent') or 0).replace(',', '').strip())
            except:
                gst_percent = 0.0
                
            try:
                mrp = float(str(data.get('mrp') or 0).replace(',', '').strip())
            except:
                mrp = 0.0

            # Create the inventory item
            item = DaftarBarang(
                user=request.user.profile,
                nama_product=name,
                part_for_what=data.get('part_for_what', ''),
                hsn_sac=data.get('hsn_sac', ''),
                jumlah_produk=qty,
                vendor=data.get('vendor', ''),
                harga_beli_satuan=purchase_price,
                laba_persen=profit_margin,
                gst_percent=gst_percent,
                mrp=mrp
            )
            
            # Download and save image
            if image_url:
                try:
                    response = requests.get(image_url, timeout=15)
                    if response.status_code == 200:
                        file_name = f"ai_{name.replace(' ', '_')}.jpg"
                        item.image.save(file_name, ContentFile(response.content), save=False)
                    else:
                        item.image = image_url
                except Exception as e:
                    print(f"Fallback to external URL string due to write/network error: {e}")
                    item.image = image_url
            
            item.save()
            return JsonResponse({'success': True, 'id': item.nomor})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def EditPart(request, part_id):
    part = get_object_or_404(JCBPart, id=part_id)
    if request.method == 'POST':
        part.part_number = request.POST.get('part_number')
        part.name = request.POST.get('name')
        part.price = request.POST.get('price', 0)
        part.category = request.POST.get('category', 'OTHER')
        part.description = request.POST.get('description', '')
        
        image = request.FILES.get('image')
        if image:
            if part.image_360_base:
                part.image_360_base.delete(save=False)
            part.image_360_base = image
            
        part.save()
        messages.success(request, f"Product '{part.name}' updated successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/data/search/'))


@login_required
def DeletePart(request, part_id):
    part = get_object_or_404(JCBPart, id=part_id)
    name = part.name
    part.delete()
    messages.success(request, f"Product '{name}' deleted successfully from catalog!")
    return redirect(request.META.get('HTTP_REFERER', '/data/search/'))


# ───────────────────────────── Vendor CRUD ─────────────────────────────

@login_required
def VendorList(request):
    vendors = Vendor.objects.all().order_by('city', 'name')
    return render(request, 'data/vendor_list.html', {'vendors': vendors})


@login_required
def VendorAdd(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        city = request.POST.get('city', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()

        if not name or not city:
            messages.warning(request, 'Vendor Name and City are required!')
            return redirect('VendorAdd')

        # Prevent duplicate name+city
        if Vendor.objects.filter(name__iexact=name, city__iexact=city).exists():
            messages.warning(request, f'Vendor "{name}" in "{city}" already exists!')
            return redirect('VendorAdd')

        Vendor.objects.create(
            name=name,
            city=city,
            contact_phone=contact_phone if contact_phone else None,
        )
        messages.success(request, f'Vendor "{name}" added successfully!')
        return redirect('VendorList')

    return render(request, 'data/vendor_add.html')


@login_required
def VendorEdit(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.name = request.POST.get('name', vendor.name).strip()
        vendor.city = request.POST.get('city', vendor.city).strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        vendor.contact_phone = contact_phone if contact_phone else None
        vendor.save()
        messages.success(request, f'Vendor "{vendor.name}" updated successfully!')
        return redirect('VendorList')

    return render(request, 'data/vendor_edit.html', {'vendor': vendor})


@login_required
def VendorDelete(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    name = vendor.name
    vendor.delete()
    messages.success(request, f'Vendor "{name}" deleted successfully!')
    return redirect('VendorList')