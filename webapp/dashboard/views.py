from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Film
from .utils import get_custom_date, calculate_top2_stats, calculate_growth


@login_required
def historic(request):
    return render(request, "dashboard/historic.html")


@login_required
def statistic(request):

    top_2 = Film.objects.filter(semaine_fr=get_custom_date("prochaine sorties")).all().order_by("-estimation")[:2]
    stats = calculate_top2_stats(top_2)
    growth = calculate_growth(stats)

    return render(request, "dashboard/statistic.html", {
        "top_2": top_2,
        "stats": stats,
        "growth": growth,
    })


@login_required
def top10(request):

    top_10 = Film.objects.filter(semaine_fr=get_custom_date("prochaine sorties")).all().order_by("-estimation")[:10]

    return render(request, "dashboard/top10.html", {
        "top_10": top_10,
    })