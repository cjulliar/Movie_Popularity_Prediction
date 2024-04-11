from django.shortcuts import render

# Create your views here.

def tmp(request):
    return render(request, 'base.html')