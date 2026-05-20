from django.urls import path
from . import views

app_name = 'livestock'  # <--- Add this line here

urlpatterns = [
    path('livestock_dashboard/', views.livestock_dashboard, name='livestock_dashboard'), # Make sure you have at least one path
]