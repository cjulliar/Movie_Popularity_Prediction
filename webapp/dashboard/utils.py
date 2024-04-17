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
    WHERE date_sortie_fr = %s
    """

    args = date_prochaine_sorties

    try:
        cur.execute(query, args)
        result = cur.fetchall()
        add_to_db(result)
    except:
        return "Erreur"

    date_prochaine_sorties = date_prochaine_sorties + timedelta(days=7)


def add_to_db(result):
    
    for row in result:
        
        film = Film(
            titre=row['titre'],
            estimation=row['estimation'],
            entrees_fr=row['entrees_fr'],
            entrees_usa=row['entrees_usa'],
            budget=row['budget'],
            salles_fr=row['salles_fr'],
            date_sortie_fr=row['date_sortie_fr'],
            data_sortie_us=row['data_sortie_us'],
            duree=row['duree'],
            pegi_fr=row['pegi_fr'],
            pegi_us=row['pegi_us'],
            franchise=row['franchise'],
            genres=row['genres'],
            pays=row['pays'],
            acteurs=row['acteurs'],
            producteur=row['producteur'],
            realisateur=row['realisateur'],
            compositeur=row['compositeur'],
            studio=row['studio']
        )

        film.save()