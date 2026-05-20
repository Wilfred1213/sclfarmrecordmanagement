from django.urls import path
from . import views

app_name = 'greenhouse' # This MUST match the namespace in the main urls.py

urlpatterns = [
    path('greenhouse_dashboard', views.greenhouse_dashboard, name='greenhouse_dashboard'),
]