from django.contrib import admin
from .models import Film

# Register your models here.

class FilmAdmin(admin.ModelAdmin):
    list_display = ("titre", "semaine_fr")


admin.site.register(Film, FilmAdmin)