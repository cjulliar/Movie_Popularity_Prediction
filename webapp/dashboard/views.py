from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Film
from .utils import date_prochaine_sorties


@login_required
def historic(request):
    return render(request, "dashboard/historic.html")


@login_required
def statistic(request):
    return render(request, "dashboard/statistic.html")


@login_required
def top10(request):

    top_10 = Film.objects.filter(date_sortie_fr=date_prochaine_sorties).all().order_by("-estimation")[:10]

    return render(request, "dashboard/top10.html", {
        "top_10": top_10,
    })