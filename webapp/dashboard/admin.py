from django.contrib import admin
from .models import CustomDate, Film

# Register your models here.

class CustomDateAdmin(admin.ModelAdmin):
    list_display = ("nom", "date")

class FilmAdmin(admin.ModelAdmin):
    list_display = ("titre", "semaine_fr")


admin.site.register(CustomDate, CustomDateAdmin)
admin.site.register(Film, FilmAdmin)