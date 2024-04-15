from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required
def historic(request):
    return render(request, "dashboard/historic.html")


@login_required
def statistic(request):
    return render(request, "dashboard/statistic.html")


@login_required
def top10(request):
    return render(request, "dashboard/top10.html")