from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Film
from .utils import get_custom_date


@login_required
def historic(request):
    return render(request, "dashboard/historic.html")


@login_required
def statistic(request):
    return render(request, "dashboard/statistic.html")


@login_required
def top10(request):

    top_10 = Film.objects.filter(semaine_fr=get_custom_date("prochaine sorties")).all().order_by("-estimation")[:10]

    return render(request, "dashboard/top10.html", {
        "top_10": top_10,
    })