from django.shortcuts import render

# Create your views here.

def hit(request):
    return render(request, 'hitlist.html')

def home(request):
    return render(request, 'hitlist.html')
