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
    path('save-ai-inventory/', views.SaveAIInventory, name='SaveAIInventory'),
    path('edit-part/<int:part_id>/', views.EditPart, name='EditPart'),
    path('delete-part/<int:part_id>/', views.DeletePart, name='DeletePart'),
    # Vendor CRUD
    path('vendor-list/', views.VendorList, name='VendorList'),
    path('vendor-add/', views.VendorAdd, name='VendorAdd'),
    path('vendor-edit/<int:vendor_id>/', views.VendorEdit, name='VendorEdit'),
    path('vendor-delete/<int:vendor_id>/', views.VendorDelete, name='VendorDelete'),
    path('vendor-price-add/', views.VendorPriceAdd, name='VendorPriceAdd'),
]


