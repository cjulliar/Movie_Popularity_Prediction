import pandas as pd
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime

# Fonctions de nettoyage des données
class Utils:
    @staticmethod
    def clean_text(text):
        if pd.isna(text):
            return None  # ou retourner une chaîne vide '', selon comment vous voulez gérer les NaN dans votre base de données
        text = text.replace("[", "").replace("]", "").replace("'", "").replace("création", "").replace('""', "")
        # Supprimer les espaces en excès et mettre en forme
        return re.sub(r'\s+', ' ', text).strip().lower()

    @staticmethod
    def clean_budget(budget):
        try:
            # Si la chaîne contient autre chose que des chiffres, des points ou des virgules, retournez None
            if re.search(r'[^0-9\.,]', str(budget)):
                return None
            # Sinon, nettoyez la chaîne et convertissez-la en un nombre entier
            cleaned_budget = re.sub(r'[^\d]', '', budget.replace(',', '.'))
            return int(float(cleaned_budget))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_date(date_str):
        if not isinstance(date_str, str) or pd.isna(date_str):
            return None  # Vous pouvez retourner une chaîne vide '' ou une autre valeur par défaut que vous souhaitez pour les dates non valides.
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None 

    @staticmethod
    def convert_to_float(value):
        """ convertie la valeurs en None pour la bdd si elle
        est un 0, N/A, None ou ''

        Args:
            value (_type_): str ou int

        Returns:
            _type_: None
        """
        if pd.isna(value) or value in ('', 'N/A', 'None', '0'):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod        
    def clean_and_convert_vote_count(vote_count):
        """ Nettoye le vote , enlève les K, M et remplace par
        valeurs numériques

        Args:
            vote_count (_type_): 10k

        Returns:
            _type_: 10 000 (float)
        """
        if 'K' in vote_count:
            vote_count = vote_count.replace('K', '')
            return float(vote_count) * 1000
        elif 'M' in vote_count:
            vote_count = vote_count.replace('M', '')
            return float(vote_count) * 1000000
        else:
            try:
                return float(vote_count)
            except ValueError:
                return None
    
    @staticmethod
    def convert_duration(duration_str):
        """ convertie la durée du film en minutes.

        Args:
            duration_str (_type_): format str '1h30'

        Returns:
            _type_: numbers
        """
        if pd.isna(duration_str) or not isinstance(duration_str, str):
            return None  # Retourne None pour les valeurs NaN ou non-chaînes
        
        # Exemple de format attendu: '1h 30min'
        match = re.match(r'(\d+)h\s+(\d+)min', duration_str)
        if not match:
            return None  # Format inattendu

        hours, minutes = match.groups()
        return int(hours) * 60 + int(minutes)
    
    @staticmethod
    def check_int(value):
        """
        Vérifie si la valeur est un entier valide représenté sous forme de chaîne. Si oui, retourne l'entier.
        Sinon, retourne None.
        """
        try:
            # Convertit la valeur en chaîne de caractères puis vérifie si elle représente un entier
            if isinstance(value, int):
                return value  # La valeur est déjà un entier
            value_str = str(value)
            # Utiliser une expression régulière pour vérifier si la chaîne est un entier
            if re.fullmatch(r'\d+', value_str):
                return int(value_str)  # Conversion de la chaîne en entier
            else:
                return None  # La chaîne n'est pas un entier
        except (ValueError, TypeError):
            return None

# Nettoyage du DataFrame
def clean_data(df):
    # Remplacer les valeurs pd.NA par None
    df.replace({pd.NA: None}, inplace=True)

    # Colonnes textuelles nécessitant un nettoyage
    text_fields = ['compositeur', 'producteur', 'realisateur', 'titre', 'genres', 'pays', 'acteurs']
    for field in text_fields:
        df[field] = df[field].apply(Utils.clean_text)

    # Vérification et conversion des années en entiers si elles sont valides
    #df['annee'] = df['annee'].apply(Utils.check_int)

    # Nettoyage et conversion spécifique de la colonne 'budget'
    #df['budget'] = df['budget'].apply(Utils.clean_budget)

    # Ajustez ici pour d'autres colonnes comme 'semaine_fr' ou 'entrees_fr' si elles sont ajoutées plus tard

    return df

# Connexion à la base de données
def connect_db():
    try:
        conn = mysql.connector.connect(user='tenshi', password='Simplon59', host='casq.mysql.database.azure.com', database='cinema_db')
        print("Connected to the database")
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Insérer ou mettre à jour une personne dans la table personnes et renvoyer son ID
def insert_person(conn, name, role, film_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT personne_id FROM personnes WHERE nom = %s", (name,))
        result = cursor.fetchone()
        if result:
            personne_id = result[0]
        else:
            cursor.execute("INSERT INTO personnes (nom) VALUES (%s)", (name,))
            personne_id = cursor.lastrowid
            conn.commit()

        # Associer la personne au film dans la table film_personne
        cursor.execute("INSERT INTO film_personne (film_id, personne_id, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role=VALUES(role)", (film_id, personne_id, role))
        conn.commit()
    except Error as e:
        print(f"Error inserting person: {e}")
        conn.rollback()
    finally:
        cursor.close()
    return personne_id

# Fonction pour insérer ou obtenir l'ID d'un studio
def insert_or_get_studio_id(conn, studio_name):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT studio_id FROM studios WHERE nom = %s", (studio_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute("INSERT INTO studios (nom) VALUES (%s)", (studio_name,))
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"Error inserting/getting studio: {e}")
        conn.rollback()
        return None
    

# Fonction pour associer un film avec un studio
def associate_film_with_studio(conn, film_id, studio_id):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO film_studio (film_id, studio_id) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE studio_id=VALUES(studio_id)", 
            (film_id, studio_id)
        )
        conn.commit()
    except Error as e:
        print(f"Error associating film with studio: {e}")
        conn.rollback()
    

# Insertion ou mise à jour des données dans la base de données
def insert_or_update_film(df, conn):
    cursor = conn.cursor()
    for index, row in df.iterrows():
        try:
            # Vérification de l'existence d'un film avec le même titre et année
            cursor.execute("SELECT film_id FROM films WHERE titre = %s AND annee = %s", (row['titre'], row['annee']))
            film_result = cursor.fetchone()
            film_id = film_result[0] if film_result else None

            # Données pour insertion/mise à jour dans la table films
            film_data = {
                'titre': row['titre'],
                'annee': row['annee'],
                'budget': row['budget'],
                'genres': row['genres'],
                'pays': row['pays'],
                'franchise': row.get('franchise', None),
                'entrees_fr': row.get('entrees_fr', None),
                'semaine_fr': row.get('semaine_fr', None)
                # Ajouter d'autres champs ici si votre CSV les contient
            }

            if film_id:  # Le film existe, donc mise à jour
                update_columns = ', '.join([f"{k} = %s" for k in film_data.keys()])
                update_values = list(film_data.values())
                update_values.append(film_id)
                cursor.execute(f"UPDATE films SET {update_columns} WHERE film_id = %s", update_values)
            else:  # Le film n'existe pas, donc insertion
                insert_columns = ', '.join(film_data.keys())
                insert_placeholders = ', '.join(['%s'] * len(film_data))
                insert_values = list(film_data.values())
                cursor.execute(f"INSERT INTO films ({insert_columns}) VALUES ({insert_placeholders})", insert_values)
                film_id = cursor.lastrowid

            

            # Insérer ou mettre à jour les relations dans la table film_personne
            for role in ['compositeur', 'producteur', 'realisateur', 'acteurs']:
                if role in row and pd.notna(row[role]):
                    for person_name in row[role].split(','):
                        insert_person(conn, person_name.strip(), role[:-1], film_id)
            
            # Après avoir inséré/mis à jour les films, gérez le studio
            if 'studio' in row and pd.notna(row['studio']):
                studio_name = row['studio']
                studio_id = insert_or_get_studio_id(conn, studio_name)
                if studio_id is not None:
                    associate_film_with_studio(conn, film_id, studio_id)

            conn.commit()
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'insertion/mise à jour du film: {e}")
            conn.rollback()
        
  

# Chargement du CSV, nettoyage et insertion en base de données
data = pd.read_csv('/home/tenshi/projets/Movie_Popularity_Prediction/ml/input_datasets/moviesdatabdd.csv')
data_cleaned = clean_data(data)
conn = connect_db()
if conn:
    insert_or_update_film(data_cleaned, conn)
    conn.close()