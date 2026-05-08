import os
import sys
import requests
import django
import time

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Monkeypatch for django-jet compatibility
import django.utils.encoding
if not hasattr(django.utils.encoding, 'python_2_unicode_compatible'):
    django.utils.encoding.python_2_unicode_compatible = lambda x: x

import collections
if not hasattr(collections, 'MutableSet'):
    import collections.abc
    collections.MutableSet = collections.abc.MutableSet
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Mapping = collections.abc.Mapping
    collections.Sequence = collections.abc.Sequence
    collections.Iterable = collections.abc.Iterable
    collections.Callable = collections.abc.Callable

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from data.models import JCBPart
from django.core.files.base import ContentFile

parts_to_update = [
    {"no": "JCB-C601", "name": "Track Roller Assembly", "prompt": "JCB excavator track roller assembly, heavy duty steel industrial part, white background, high detail"},
    {"no": "JCB-C602", "name": "Idler Wheel", "prompt": "heavy duty idler wheel for JCB excavator, large steel wheel, industrial machinery part, white background"},
    {"no": "JCB-L701", "name": "Head Light Assembly", "prompt": "JCB excavator headlight assembly, glass lens, protective grille, industrial lighting, white background"},
    {"no": "JCB-L702", "name": "Rear Work Light LED", "prompt": "square LED work light for JCB machinery, black aluminum housing, industrial light, white background"},
    {"no": "JCB-H303", "name": "Hydraulic Oil Filter Element", "prompt": "JCB hydraulic oil filter element, metal mesh, industrial filtration part, white background"},
    {"no": "JCB-E401", "name": "Engine Oil Filter", "prompt": "yellow engine oil filter for JCB machinery, spin-on filter, white background"},
    {"no": "JCB-G501", "name": "Bucket Teeth (Set of 5)", "prompt": "set of 5 steel bucket teeth for JCB excavator, heavy duty excavator parts, white background"},
    {"no": "JCB-G502", "name": "Side Cutter Pair", "prompt": "pair of steel side cutters for JCB excavator bucket, industrial machinery parts, white background"},
    {"no": "JCB-H301", "name": "Hydraulic Cylinder Seal Kit", "prompt": "hydraulic cylinder seal kit for JCB, rubber o-rings and seals set, industrial kit, white background"},
    {"no": "JCB-E402", "name": "Fuel Injection Pump", "prompt": "diesel fuel injection pump for JCB engine, complex mechanical part, white background"},
    {"no": "JCB-E403", "name": "Turbocharger Assembly", "prompt": "turbocharger assembly for JCB engine, metallic industrial part, white background"},
]

def update_images():
    for item in parts_to_update:
        part_no = item['no']
        # Using tags and a unique seed (lock) for different images
        tags = item['name'].lower().replace(" ", ",")
        # Adding lock={part_no} to ensure different images for each part
        image_url = f"https://loremflickr.com/512/512/excavator,machinery,{tags}/all?lock={hash(part_no)}"
        
        try:
            print(f"Fetching unique image for {part_no}: {item['name']}...")
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                part = JCBPart.objects.filter(part_number=part_no).first()
                if part:
                    filename = f"{part_no}.jpg"
                    part.image_360_base.save(filename, ContentFile(response.content), save=True)
                    print(f"Successfully updated {part_no} with unique image")
                else:
                    print(f"Part {part_no} not found.")
            else:
                print(f"Failed for {part_no}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        time.sleep(1)

if __name__ == "__main__":
    update_images()
