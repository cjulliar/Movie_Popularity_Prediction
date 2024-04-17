from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    pass


class Film(models.Model):
    titre = models.CharField(max_length=1000)
    estimation = models.PositiveIntegerField(null=True, blank=True)
    entrees_fr = models.PositiveIntegerField(null=True, blank=True)
    entrees_usa = models.PositiveIntegerField(default=0, null=True, blank=True)
    budget = models.PositiveIntegerField(null=True, blank=True)
    salles_fr = models.PositiveIntegerField(null=True, blank=True)
    date_sortie_fr = models.DateField(null=True, blank=True)
    data_sortie_us = models.DateField(null=True, blank=True)
    duree = models.PositiveIntegerField(null=True, blank=True)
    pegi_fr = models.CharField(max_length=100, null=True, blank=True)
    pegi_us = models.CharField(max_length=100, null=True, blank=True)
    franchise = models.BooleanField(null=True, blank=True)
    genres = models.CharField(max_length=1000, null=True, blank=True) 
    pays = models.CharField(max_length=100, null=True, blank=True)
    affiche = models.ImageField(upload_to="affiches", null=True, blank=True)
    synopsis = models.TextField(default="Pas de synopsis")
# BDD avec table unique
    acteurs = models.CharField(max_length=1000, null=True, blank=True)
    producteur = models.CharField(max_length=100, null=True, blank=True)
    realisateur = models.CharField(max_length=100, null=True, blank=True)
    compositeur = models.CharField(max_length=100, null=True, blank=True)
    studio = models.CharField(max_length=100, null=True, blank=True)
    

# BDD avec plusieurs tables

    # personnes = models.ManyToManyField("Personne", related_name="films_de_la_personne")
    # studio = models.ForeignKey("Studio", on_delete=models.PROTECT, related_name="films_du_studio")


# class Personne(models.Model):
#     nom = models.CharField(max_length=100)
#     role = models.CharField(max_length=100)


# class Studio(models.Model):
#     nom = models.CharField(max_length=100)