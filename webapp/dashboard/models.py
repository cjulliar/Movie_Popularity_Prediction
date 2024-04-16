from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    pass


class Film(models.Model):
    titre = models.CharField(max_length=1000)
    estimation = models.PositiveIntegerField()
    entrees_fr = models.PositiveIntegerField()
    entrees_usa = models.PositiveIntegerField(default=0)
    budget = models.PositiveIntegerField()
    salles_fr = models.PositiveIntegerField()
    date_sortie_fr = models.DateField()
    data_sortie_us = models.DateField()
    duree = models.PositiveIntegerField()
    pegi_fr = models.CharField(max_length=100)
    pegi_us = models.CharField(max_length=100)
    franchise = models.BooleanField()
    genres = models.CharField(max_length=1000) 
    pays = models.CharField(max_length=100)
    affiche = models.ImageField()
    synopsis = models.TextField()
# BDD avec table unique
    acteurs = models.CharField(max_length=1000)
    producteur = models.CharField(max_length=100)
    realisateur = models.CharField(max_length=100)
    compositeur = models.CharField(max_length=100)
    studio = models.CharField(max_length=100)
    

# BDD avec plusieurs tables

    # personnes = models.ManyToManyField("Personne", related_name="films_de_la_personne")
    # studio = models.ForeignKey("Studio", on_delete=models.PROTECT, related_name="films_du_studio")


# class Personne(models.Model):
#     nom = models.CharField(max_length=100)
#     role = models.CharField(max_length=100)


# class Studio(models.Model):
#     nom = models.CharField(max_length=100)