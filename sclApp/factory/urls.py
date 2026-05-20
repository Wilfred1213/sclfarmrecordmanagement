from django.urls import path
from . import views

app_name = 'factory'  # <--- Add this line here

urlpatterns = [
    path('', views.index, name='index'), # Make sure you have at least one path
]