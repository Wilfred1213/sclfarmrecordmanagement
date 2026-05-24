from django.shortcuts import render

# Create your views here.
def loggin(request):
    # This renders your login template instead of returning None
    return render(request, 'accounts/login.html')