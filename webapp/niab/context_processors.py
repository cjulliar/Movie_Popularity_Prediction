from dashboard.utils import date_prochaine_sorties

def global_context(request):
    return {
        'date_semaine': date_prochaine_sorties,
    }