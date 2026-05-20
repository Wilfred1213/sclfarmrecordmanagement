from django.urls import path

from sclApp.medical import views 

app_name = 'medical' 
 
urlpatterns = [
    path('staff_medical_dashboard/', views.staff_medical_dashboard, name='staff_medical_dashboard'),
    
]