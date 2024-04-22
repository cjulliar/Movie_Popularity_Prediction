from dashboard.utils import get_custom_date

def global_context(request):
    return {
        'date_semaine': get_custom_date("prochaine sorties"),
    }