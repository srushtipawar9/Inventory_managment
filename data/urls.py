from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.GlobalSearch, name='GlobalSearch'),
    path('part/<int:part_id>/', views.PartDetail, name='PartDetail'),
    path('upload/', views.StockUpload, name='StockUpload'),
    path('import-amazon/', views.ImportAmazonPart, name='ImportAmazonPart'),
]
