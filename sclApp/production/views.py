from django.shortcuts import render

def production_home(request):
    return render(request, 'production/greenhouse.html')

