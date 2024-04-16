import os
from datetime import datetime, timedelta

from .models import Film

import mysql.connector


date_prochaine_sorties = datetime.strftime("2024-04-17", '%Y-%m-%d')


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
def get_movies(cur):

    query = """
    SELECT * FROM films 
    WHERE semaine_fr = %s
    """

    args = date_prochaine_sorties

    cur.execute(query, args)
    result = cur.fetchall()
    add_to_db(result)

    date_prochaine_sorties = date_prochaine_sorties + timedelta(days=7)


def add_to_db(result):
    
    for row in result:
        film = Film(
            titre=row['titre'],
            estimation_entrees_fr=row['estimation_entrees_fr'],
            entrees_fr=row['entrees_fr'],
            recettes_us_1er_weekend=row['recettes_us_1er_weekend'],
            budget=row['budget'],
            salles_fr=row['salles_fr'],
            genres=row['genres'],
            pays=row['pays'],
            duree=row['duree'],
            franchise=row['franchise'],
            semaine_fr=row['semaine_fr'],
            semaine_usa=row['semaine_usa'],
            annee=row['annee'],
            pegi_fr=row['pegi_fr'],
            pegi_usa=row['pegi_usa'],
            studio_id=row['studio_id']
        )

    film.save()