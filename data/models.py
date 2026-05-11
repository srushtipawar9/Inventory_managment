from __future__ import absolute_import, unicode_literals
from django.db import models
from django.utils import timezone
# Create your models here.
class Stock(models.Model):

    name = models.CharField(max_length=100, unique=True)
    price = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name
class JCBPart(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    
    # For 360 view - we can store multiple images or a sequence
    image_360_base = models.ImageField(upload_to='parts/360/', blank=True, null=True)
    # Alternatively, a JSON or related model for multiple frames
    
    CATEGORY_CHOICES = [
        ('HYDRAULICS', 'Hydraulics'),
        ('POWERTRAIN', 'Powertrain (Engines & Transmission)'),
        ('GET', 'Ground Engaging Tools (Teeth & Blades)'),
        ('FILTERS', 'Filters'),
        ('ELECTRICAL', 'Electrical & Lighting'),
        ('CHASSIS', 'Chassis & Undercarriage'),
        ('OTHER', 'Other Spare Parts'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.part_number} - {self.name}"


class Vendor(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'city')
        ordering = ('city', 'name')

    def __str__(self):
        return f"{self.name} ({self.city})"


class VendorPartPrice(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='part_prices')
    part = models.ForeignKey(JCBPart, on_delete=models.CASCADE, related_name='vendor_prices')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vendor', 'part')
        ordering = ('part__category', 'part__name', 'vendor__city', 'vendor__name')

    def __str__(self):
        return f"{self.vendor} - {self.part.part_number}: {self.price}"
