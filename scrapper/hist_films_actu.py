import numpy as np
import pandas as pd
import pickle
import mysql.connector

# Informations de connexion à la base de données
host = "casq.mysql.database.azure.com"
user = "tenshi"
password = "Simplon59"
database = "db_movies"

# Connexion à la base de données
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Requête SQL pour extraire les données
sql_query = "SELECT * FROM test;"
# sql_query = "SELECT f.*, s.nom AS 'studio_name', p_realisateur.nom AS 'realisateur_nom', p_compositeur.nom AS 'compositeur_nom', p_producteur.nom AS 'producteur_nom', p_acteur.nom AS 'acteur_nom' FROM films f JOIN film_studio fs ON f.film_id = fs.film_id JOIN studios s ON s.studio_id = fs.studio_id JOIN film_personne fp_realisateur ON fp_realisateur.film_id = f.film_id AND fp_realisateur.role = 'realisateur' JOIN personnes p_realisateur ON p_realisateur.personne_id = fp_realisateur.personne_id JOIN film_personne fp_compositeur ON fp_compositeur.film_id = f.film_id AND fp_compositeur.role = 'compositeur' JOIN personnes p_compositeur ON p_compositeur.personne_id = fp_compositeur.personne_id JOIN film_personne fp_producteur ON fp_producteur.film_id = f.film_id AND fp_producteur.role = 'producteur' JOIN personnes p_producteur ON p_producteur.personne_id = fp_producteur.personne_id JOIN film_personne fp_acteur ON fp_acteur.film_id = f.film_id AND fp_acteur.role = 'acteur' JOIN personnes p_acteur ON p_acteur.personne_id = fp_acteur.personne_id;"

# Lecture des données dans un DataFrame pandas
data = pd.read_sql(sql_query, conn)

# Fermeture de la connexion à la base de données
conn.close()

# Enregistrement des données dans un fichier CSV
data.to_csv("datasets/donnees_SQL.csv", index=False)

with open("models/model_cb.pkl", "rb") as f:
    model = pickle.load(f)
f.close()

data['estimation'].fillna(-1, inplace=True)

types_de_donnees = {
    # 'titre': 'object',
    # 'budget': 'float64',
    # 'compositeur': 'object',
    # 'semaine_fr': 'object',
    # 'semaine_usa': 'object',
    # 'duree': 'int64',
    # 'entrees_fr': 'int64',
    # 'franchise': 'int64',
    # 'genres': 'object',
    # 'pegi_fr': 'object',
    # 'pegi_usa': 'object',
    # 'entrees_usa': 'float64',
    # 'salles_fr': 'float64',
    # 'studio': 'object',
    'estimation' : 'int64'
}
data = data.astype(types_de_donnees)

cols_drop = ["acteurs", "producteur", "realisateur","synopsis", "images"]
data = data.drop(cols_drop, axis=1)




data['budget'] = data['budget'].astype(str).str.replace('.0', '')
data['entrees_usa'] = data['entrees_usa'].astype(str).str.replace('.0', '')
data['salles_fr'] = data['salles_fr'].astype(str).str.replace('.0', '')


data['is_compositeur'] = data['compositeur'].apply(lambda x: 1 if x is not None else 0)

data['annee'] = data['semaine_fr'].astype(str).str.slice(0, 4).astype(int)

data["franchise"] = data["franchise"].astype(str)

data = data.loc[data['genres'] != -1]


data["origine"] = data["pays"]
autres_pays = data[(data["pays"] != "etats-unis") & (data["pays"] != "france")]
data.loc[autres_pays.index, "origine"] = "Autre"
cols_drop = ["pays"]
data = data.drop(cols_drop, axis=1)

data.replace('None', None, inplace=True)


# data['salles_fr'] = data['salles_fr'].astype(str).str.replace('.0', '')
# data['salles_fr'] = data['salles_fr'].str.replace(' ', '')
# data['salles_fr'].replace('-', np.nan, inplace=True)
# # Convertir la colonne en float
# data['salles_fr'] = data['salles_fr'].astype(float)
# # Remplacer les NaN par -1
# data['salles_fr'].fillna(-1, inplace=True)
# # Convertir en entie
# data['salles_fr'] = data['salles_fr'].astype(int)
# data = data[data['salles_fr'] != -1]
# # Réinitialiser l'index si nécessaire
# data.reset_index(drop=True, inplace=True)


# Connexion à la base de données
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Créer un curseur pour exécuter les requêtes SQL
cursor = conn.cursor()

# Itérer sur chaque ligne du DataFrame
for index, row in data.iterrows():
    # Créer un DataFrame pour la prédiction
    inputs = pd.DataFrame({
        'budget': [row['budget']],
        'duree': [row['duree']],
        'franchise': [row['franchise']],
        'genres': [row['genres']],
        'pegi_fr': [row['pegi_fr']],
        'pegi_usa': [row['pegi_usa']],
        'entrees_usa': [row['entrees_usa']],
        'salles_fr': [row['salles_fr']],
        'studio': [row['studio']],
        'is_compositeur': [row['is_compositeur']],
        'annee': [row['annee']],
        'origine': [row['origine']],
    })

    # Prédire le nombre d'entrées pour cette ligne
    predicted_entries = model.predict(inputs)

    # Ajouter la prédiction à la liste des prédictions
    prediction = str(predicted_entries[0])  # Convertir en int standard Python
    print(prediction)
    # Mettre à jour la base de données avec la prédiction
    film_id = row['id']  # Supposons que 'id' soit la clé primaire de la table
    cursor.execute("UPDATE test SET estimation = %s WHERE id = %s", (prediction, film_id))

# Valider la transaction et fermer le curseur
conn.commit()
cursor.close()

# Fermer la connexion à la base de données
conn.close()

