from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.top10, name='top10'),
    path('historique', views.historic, name='historic'),
    path('statistiques', views.statistic, name='statistic'),
]