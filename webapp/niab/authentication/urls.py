from django.urls import path, include
from authentication import views

app_name = 'authentication'

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
]
