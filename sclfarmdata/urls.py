"""
URL configuration for sclfarmdata project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Using 'namespace' allows you to use {% url 'production:index' %} in templates
    path('', include('sclApp.production.urls', namespace='production')),
    path('inventory/', include('sclApp.inventory.urls', namespace='inventory')),
    path('livestock/', include('sclApp.livestock.urls', namespace='livestock')),
    path('factory/', include('sclApp.factory.urls', namespace='factory')),

    path('accounts/', include('sclApp.accounts.urls', namespace='authentications')),
    path('greenhouse/', include('sclApp.greenhouse.urls', namespace='greenhouse')),
    path('medical/', include('sclApp.medical.urls', namespace='medical')),
]
# if settings.DEBUG:
#     urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns