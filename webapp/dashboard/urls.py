from django.urls import path
from dashboard import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard'

urlpatterns = [
    path('', views.top10, name='top10'),
    path('historique', views.historic, name='historic'),
    path('statistiques', views.statistic, name='statistic'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)