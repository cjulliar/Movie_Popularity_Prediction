import os
from datetime import timedelta

from .models import Film, CustomDate

import mysql.connector


def get_custom_date(name):
    "Récupere la date pour les précédentes ou prochaines sorties"
    try:
        date_prochaine_sorties = CustomDate.objects.get(nom=name)
        return date_prochaine_sorties.date
    except CustomDate.DoesNotExist:
        return None


def update_custom_dates():
    """Met à jour les dates des précedentes et prochaines sorties"""
    try:
        prochaine_sorties = CustomDate.objects.get(nom="prochaine sorties")
        precedente_sorties = CustomDate.objects.get(nom="precedente sorties")

        precedente_sorties.date = prochaine_sorties.date
        
        date_prochaine = prochaine_sorties.date
        date_prochaine += timedelta(days=7)
        prochaine_sorties.date = date_prochaine.strftime('%Y-%m-%d')

        precedente_sorties.save()
        prochaine_sorties.save()

    except:
        pass


def get_database(func):
    """Decorateur qui initialise la connexion avec la bdd mysql, lance une action sur la bdd puis ferme la connexion"""

    def wrap(*args, **kargs):

        conn = mysql.connector.connect(
        host= os.getenv("HOST_MYSQL"),
        user=os.getenv("USER_MYSQL"),
        password=os.getenv("PASSWORD_MYSQL"),
        database=os.getenv("DATABASE_MYSQL")
        )
        cur = conn.cursor()
        result = func(*args, *kargs, cur)
        conn.commit()
        conn.close()
        return result
    return wrap


@get_database
def get_initial_movies(cur):
    """Récupere de la bdd mysql les infos sur des films pour initialiser la bdd de Django"""

    date_args = ["2024-04-10", "2024-04-17"]
    for date in date_args:
        try:
            query = """
            SELECT * FROM films_hist
            WHERE semaine_fr = %s
            ORDER BY estimation DESC
            LIMIT 10
            """
            args = (date,)
            cur.execute(query, args)
            result = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            add_to_db(result, columns)
        except:
            return "Erreur"


@get_database
def get_next_movies(cur):
    """Récupere de la bdd mysql le top 10 des prochaines sorties"""
    try:
        query = """
        SELECT * FROM predict_films 
        WHERE semaine_fr = %s
        ORDER BY estimation DESC
        LIMIT 10
        """
        args = (get_custom_date("prochaine sorties"),)
        cur.execute(query, args)
        result = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        add_to_db(result, columns)

    except:
        print("Erreur")
    

@get_database
def get_old_movies(cur):
    """Récupere de la bdd mysql les infos manquantes du top 10 de la semaine précédente"""
    try:
        query = """
        SELECT * FROM films_hist
        WHERE semaine_fr = %s
        """
        args = (get_custom_date("precedente sorties"),)
        cur.execute(query, args)
        result = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        update_db(result, columns) 
    except:
        return "Erreur"
    

def add_to_db(result, columns):
    """Ajoute les prochaines sorties à la bdd de Django"""

    for row in result:
        try:
            film = Film(
                titre = row[columns.index('titre')],
                estimation = row[columns.index('estimation')],
                entrees_fr = row[columns.index('entrees_fr')],
                entrees_usa = row[columns.index('entrees_usa')],
                budget = row[columns.index('budget')],
                salles_fr = row[columns.index('salles_fr')],
                semaine_fr = row[columns.index('semaine_fr')],
                semaine_usa = row[columns.index('semaine_usa')],
                duree = row[columns.index('duree')],
                pegi_fr = row[columns.index('pegi_fr')],
                pegi_usa = row[columns.index('pegi_usa')],
                franchise = row[columns.index('franchise')],
                genres = row[columns.index('genres')],
                pays = row[columns.index('pays')],
                synopsis = row[columns.index('synopsis')],
                image_url = row[columns.index('images')],
                acteurs = row[columns.index('acteurs')],
                producteur = row[columns.index('producteur')],
                realisateur = row[columns.index('realisateur')],
                compositeur = row[columns.index('compositeur')],
                studio = row[columns.index('studio')],
            )
            film.save()
        except:
            print("Erreur pendant ajout des données")


def update_db(result, columns):
    """Met à jour les informations des précendentes sorties dans la bdd de Django"""
    last_films = Film.objects.filter(date_sortie_fr=get_custom_date("precedente sorties")).all()

    for row in result:
        try:
            film = last_films.get(titre=row[columns.index('titre')])
            film.entrees_fr = row[columns.index('entrees_fr')]
            film.entrees_usa = row[columns.index('entrees_usa')]
            film.save()
        except:
            pass


def calculate_top2_stats(top_2):

    stats = {}
    stats["recette_hebdo"] = top_2[0].estimation_recette_hebdo() + top_2[1].estimation_recette_hebdo()
    stats["benefice"] = stats["recette_hebdo"] - 4900
    stats["occup_salle_1"] = (top_2[0].estimation_quoti_niab() / 120) * 100
    stats ["occup_salle_2"] = (top_2[1].estimation_quoti_niab() / 80) * 100

    return stats


def calculate_growth(stats):

    stats = stats
    prev_stats = calculate_top2_stats(Film.objects.filter(semaine_fr=get_custom_date("precedente sorties")).all().order_by("-estimation")[:2])
    growth = ((stats["recette_hebdo"] - prev_stats["recette_hebdo"]) / prev_stats["recette_hebdo"]) * 100
    return growth


def get_last_month_dates():

    dates = []
    dates.append(get_custom_date("prochaine sorties"))

    for prev_week in range(3):

        prochaine_sorties = CustomDate.objects.get(nom="prochaine sorties")
        precedente_sorties = CustomDate.objects.get(nom="precedente sorties")

        precedente_sorties.date = prochaine_sorties.date
        
        date_prochaine = prochaine_sorties.date
        date_prochaine += timedelta(days=7)
        prochaine_sorties.date = date_prochaine.strftime('%Y-%m-%d')
        pass