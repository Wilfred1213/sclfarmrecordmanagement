from django.urls import path
from . import views

app_name = 'authentications' # This must match the namespace in your main urls.py

urlpatterns = [
    # Add your login/profile paths here later
    path('login/', views.login, name='login'),
]