from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
import requests
from .resources import StockResource

from tablib import Dataset
from .models import JCBPart, Stock, VendorPartPrice
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
    Compare vendor prices across cities and highlight cheapest/most-expensive.
    """
    category = (request.GET.get("category") or "HYDRAULICS").upper()
    if category not in ("HYDRAULICS", "ALL"):
        category = "HYDRAULICS"

    prices_qs = (
        VendorPartPrice.objects.select_related("vendor", "part")
        .all()
        .order_by("part__category", "part__name", "vendor__city", "vendor__name")
    )
    if category != "ALL":
        prices_qs = prices_qs.filter(part__category=category)

    # Group by part
    parts_map = {}
    for vp in prices_qs:
        p = vp.part
        entry = parts_map.get(p.id)
        if not entry:
            entry = {
                "part": p,
                "rows": [],
                "min_price": None,
                "max_price": None,
            }
            parts_map[p.id] = entry
        entry["rows"].append(vp)

    # Precompute min/max per part
    for entry in parts_map.values():
        prices = [r.price for r in entry["rows"]]
        entry["min_price"] = min(prices) if prices else None
        entry["max_price"] = max(prices) if prices else None

    context = {
        "category": category,
        "parts_entries": list(parts_map.values()),
    }

    if request.GET.get("format") == "json" or request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("data/vendors_partial.html", context, request=request)
        return JsonResponse({"html": html, "category": category})

    return render(request, "data/vendors.html", context)

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