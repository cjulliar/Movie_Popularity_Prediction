import os
from datetime import datetime, timedelta

from .models import Film

import mysql.connector


date_prochaine_sorties = "2024-04-17"


def update_release_date():

    global date_prochaine_sorties
    
    date_prochaine_sorties = datetime.strptime(date_prochaine_sorties, '%Y-%m-%d')
    date_prochaine_sorties = date_prochaine_sorties.strftime('%Y-%m-%d')
    date_prochaine_sorties = date_prochaine_sorties + timedelta(days=7)


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

    try:

        update_release_date()

        query = """
        SELECT * FROM predict_films 
        WHERE semaine_fr = %s
        """

        args = date_prochaine_sorties

        cur.execute(query, args)
        result = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        add_to_db(result, columns)

    except:
        return "Erreur"
    

def add_to_db(result, columns):
    
    for row in result:
        
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