from django.shortcuts import render, get_object_or_404
from .resources import StockResource
from tablib import Dataset
from .models import JCBPart, Stock
from django.db.models import Q

def GlobalSearch(request):
    query = request.GET.get('q')
    results = []
    if query:
        # Search in JCBPart
        parts_list = JCBPart.objects.filter(
            Q(name__icontains=query) | Q(part_number__icontains=query) | Q(description__icontains=query)
        ).order_by('category')
        
        # Group parts by category for better UI
        categorized_parts = {}
        for part in parts_list:
            cat_name = part.get_category_display()
            if cat_name not in categorized_parts:
                categorized_parts[cat_name] = []
            categorized_parts[cat_name].append(part)
            
        # Search in Stock
        stocks = Stock.objects.filter(name__icontains=query)
        
        # --- Amazon Marketplace Integration ---
        import requests
        amazon_results = []
        extra_parts = []
        headers = {
            "x-rapidapi-key": "a536bdbeafmshfc70cd8bb5336c9p146880jsnc8af7367cb7a",
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
        }
        
        try:
            # Reverting to simpler query for better reliability
            url = "https://real-time-amazon-data.p.rapidapi.com/search"
            querystring = {"query": query, "page": "1", "country": "IN", "sort_by": "RELEVANCE"}
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            if response.status_code == 200:
                amazon_results = response.json().get('data', {}).get('products', [])[:8]
                
        except Exception as e:
            print(f"Amazon API Error: {e}")
        
        results = {
            'categorized_parts': categorized_parts,
            'stocks': stocks,
            'amazon_results': amazon_results,
            'extra_parts': [],
            'jcb_products': [],
            'query': query,
            'has_parts': len(parts_list) > 0
        }
    return render(request, 'data/search_results.html', results)

def PartDetail(request, part_id):
    part = get_object_or_404(JCBPart, id=part_id)
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
                    from django.core.files.temp import NamedTemporaryFile
                    
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Create a filename from ASIN
                        img_filename = f"{data.get('asin', 'part')}.jpg"
                        new_part.image_360_base.save(img_filename, ContentFile(img_response.content), save=True)
                except Exception as e:
                    print(f"CRITICAL: Image download error: {e}")

            new_part.save()
            
            return JsonResponse({'success': True, 'already_exists': False, 'part_id': new_part.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def MasterCatalog(request):
    parts = JCBPart.objects.all().order_by('category', 'name')
    return render(request, 'data/master_catalog.html', {'parts': parts})