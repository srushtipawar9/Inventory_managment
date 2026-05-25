from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeIndex, name='HomeIndex'),
    path('stock/', views.TotalStock, name='TotalStock'),
    path('stock/edit/<int:pk>/', views.EditStock, name='EditStock'),
    path('stock/delete/<int:pk>/', views.DeleteStock, name='DeleteStock'),
    path('stock/hide/<int:pk>/', views.HideStock, name='HideStock'),
    path('stock/unhide/<int:pk>/', views.UnhideStock, name='UnhideStock'),
    path('input/', views.InputStock, name='InputStock'),
    path('cart/', views.Cart, name='Cart'),
    path('struck/<int:pk>/', views.StruckPembelian, name='StruckPembelian'),
    path('purchase/', views.DaftarPembelian, name='DaftarPembelian'),
    path('report/', views.ReportView, name='ReportView'),
    path('estimate/', views.EstimateView, name='EstimateView'),
    path('estimate/part-price/', views.PartPriceLookup, name='PartPriceLookup'),
    path('estimate/part-suggestions/', views.PartSuggestions, name='PartSuggestions'),
    path('estimate/save/', views.SaveEstimate, name='SaveEstimate'),
]

handler500 = 'cashier.views.handler500'