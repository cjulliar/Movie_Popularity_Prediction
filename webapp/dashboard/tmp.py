import pandas as pd

from .models import Film


def tmp_db_fullfill():

    data = pd.read_csv("tmp/next_movies_details.csv", sep=";")
    
    for index, row in data.iterrows():

        film = Film(
        titre=row['titre'],
        duree=row['duree'],
        genres=row['genres'],
        pegi_fr=row['pegi_fr'],
        salles_fr=row['salles_fr'],
        studio=row['studio'],
        pays=row['origine'],
        realisateur=row['realisateur'],
        acteurs=row['acteurs'],
        synopsis = row['synopsis']
        )

        film.save()