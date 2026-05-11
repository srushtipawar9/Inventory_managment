from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.GlobalSearch, name='GlobalSearch'),
    path('part/<int:part_id>/', views.PartDetail, name='PartDetail'),
    path('upload/', views.StockUpload, name='StockUpload'),
    path('import-amazon/', views.ImportAmazonPart, name='ImportAmazonPart'),
    path('catalog/', views.MasterCatalog, name='MasterCatalog'),
    path('vendors/', views.VendorComparison, name='VendorComparison'),
    path('remove-image/<int:part_id>/', views.RemovePartImage, name='RemovePartImage'),
    path('quick-add/', views.QuickAddProduct, name='QuickAddProduct'),
]
