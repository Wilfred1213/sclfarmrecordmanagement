from django.urls import path
from . import views

app_name = 'production' # This MUST match the namespace in the main urls.py

urlpatterns = [
    path('', views.production_home, name='index'),
]