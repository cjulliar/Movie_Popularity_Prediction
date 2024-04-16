from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    pass


class Film(models.Model):
    titre = models.CharField(max_length=1000)
    estimation_entrees_fr = models.PositiveIntegerField()
    entrees_fr = models.PositiveIntegerField()
    recettes_us_1er_weekend = models.PositiveIntegerField(default=0)
    budget = models.PositiveIntegerField()
    salles_fr = models.PositiveIntegerField()
    genres = models.CharField(max_length=1000) 
    pays = models.CharField(max_length=100)
    duree = models.PositiveIntegerField()
    franchise = models.BooleanField()
    semaine_fr = models.DateField()
    semaine_usa = models.DateField()
    annee = models.DateField()
    pegi_fr = models.CharField(max_length=100)
    pegi_usa = models.CharField(max_length=100)
    affiche = models.ImageField() 
    personnes = models.ManyToManyField("Personne", related_name="films_de_la_personne")
    studio = models.ForeignKey("Studio", on_delete=models.PROTECT, related_name="films_du_studio")


class Personne(models.Model):
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=100)


class Studio(models.Model):
    nom = models.CharField(max_length=100)