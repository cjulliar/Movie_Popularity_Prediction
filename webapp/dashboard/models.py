from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    pass


class CustomDate(models.Model):
    nom = models.CharField(max_length=1000)
    date = models.DateField(null=True, blank=True)


class Film(models.Model):
    titre = models.CharField(max_length=1000)
    estimation = models.PositiveIntegerField(null=True, blank=True)
    entrees_fr = models.PositiveIntegerField(null=True, blank=True)
    entrees_usa = models.PositiveIntegerField(default=0, null=True, blank=True)
    budget = models.PositiveIntegerField(null=True, blank=True)
    salles_fr = models.PositiveIntegerField(null=True, blank=True)
    semaine_fr = models.DateField(null=True, blank=True)
    semaine_usa = models.DateField(null=True, blank=True)
    duree = models.PositiveIntegerField(null=True, blank=True)
    pegi_fr = models.CharField(max_length=1000, null=True, blank=True)
    pegi_usa = models.CharField(max_length=1000, null=True, blank=True)
    franchise = models.BooleanField(null=True, blank=True)
    genres = models.CharField(max_length=1000, null=True, blank=True) 
    pays = models.CharField(max_length=1000, null=True, blank=True)
    synopsis = models.TextField(default="Pas de synopsis", null=True, blank=True)
    #affiche = models.ImageField(upload_to="affiches", null=True, blank=True)
    image_url = models.CharField(max_length=1000, null=True, blank=True)
# BDD avec table unique
    acteurs = models.CharField(max_length=1000, null=True, blank=True)
    producteur = models.CharField(max_length=1000, null=True, blank=True)
    realisateur = models.CharField(max_length=1000, null=True, blank=True)
    compositeur = models.CharField(max_length=1000, null=True, blank=True)
    studio = models.CharField(max_length=1000, null=True, blank=True)

    def estimation_hebdo_niab(self):
        """Estimation du nombres d'entrees sur la semaine pour le cinema NIAB (1/2000 du traffic national)"""
        estimation = self.estimation / 2000
        return estimation

    def estimation_quoti_niab(self):
        """Estimation du nombres d'entrees quotidienne sur la semaine pour le cinema NIAB (1/2000 du traffic national)"""
        estimation = self.estimation_hebdo_niab() / 7
        return estimation
    
    def estimation_recette_hebdo(self):
        estimation = self.estimation_hebdo_niab() * 10
        return estimation
    

    

# BDD avec plusieurs tables

    # personnes = models.ManyToManyField("Personne", related_name="films_de_la_personne")
    # studio = models.ForeignKey("Studio", on_delete=models.PROTECT, related_name="films_du_studio")


# class Personne(models.Model):
#     nom = models.CharField(max_length=100)
#     role = models.CharField(max_length=100)


# class Studio(models.Model):
#     nom = models.CharField(max_length=100)