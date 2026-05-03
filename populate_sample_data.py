import os
import django
import sys

# Add the project directory to sys.path
sys.path.append('d:/inventort-managment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crm.models import Customer
from data.models import JCBPart

def populate():
    # Add a customer with dues
    c1, created = Customer.objects.get_or_create(
        name="Rahul Sharma",
        phone="9876543210",
        email="rahul@example.com",
        outstanding_balance=15500.50
    )
    if created:
        print(f"Created customer: {c1.name}")

    c2, created = Customer.objects.get_or_create(
        name="Amit Patel",
        phone="9988776655",
        email="amit@example.com",
        outstanding_balance=0.00
    )
    if created:
        print(f"Created customer: {c2.name}")

    # Add JCB parts
    p1, created = JCBPart.objects.get_or_create(
        part_number="JCB-G101",
        name="Main Drive Gear",
        description="High-durability main drive gear for JCB 3DX backhoe loader.",
        price=1250.00,
        stock_quantity=15
    )
    if created:
        print(f"Created part: {p1.name}")

    p2, created = JCBPart.objects.get_or_create(
        part_number="JCB-H202",
        name="Hydraulic Pump Seal Kit",
        description="Complete seal kit for JCB hydraulic pumps, compatible with multiple models.",
        price=450.00,
        stock_quantity=20
    )
    if created:
        print(f"Created part: {p2.name}")

if __name__ == "__main__":
    populate()
