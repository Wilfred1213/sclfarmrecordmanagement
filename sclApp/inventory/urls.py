from django.urls import path
from . import views

app_name = 'inventory'  # <--- Add this line here

urlpatterns = [
    path('inventory_dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('mark_as_returned/<int:transaction_id>/', views.mark_as_returned, name='mark_as_returned')
]