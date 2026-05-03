from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.CustomerList, name='CustomerList'),
    path('customers/add/', views.CustomerAdd, name='CustomerAdd'),
    path('customers/edit/<int:customer_id>/', views.CustomerEdit, name='CustomerEdit'),
    path('customers/delete/<int:customer_id>/', views.CustomerDelete, name='CustomerDelete'),
    path('reminder/<int:customer_id>/', views.SendReminder, name='SendReminder'),
]
