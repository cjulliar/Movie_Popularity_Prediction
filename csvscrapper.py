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
    def clean_entrees(entrees_str):
        """
        Nettoie la chaîne de caractères représentant le nombre d'entrées aux États-Unis et France et la convertit en entier.

        Args:
            entrees_usa_str (str): Chaîne de caractères représentant le nombre d'entrées aux États-Unis et en France

        Returns:
            int: Nombre d'entrées aux États-Unis et France, None si la chaîne n'est pas un nombre valide
        """
        try:
            if pd.isna(entrees_str):
                return 'NULL'
            # Supprimer les espaces et le signe '$'
            entrees_str = entrees_str.replace(' ', '').replace('$', '')
            return int(entrees_str)
        except ValueError:
            return 'NULL'
    
    @staticmethod
    def clean_salles_fr(salles_fr_str):
        """
        Nettoie la chaîne de caractères représentant le nombre de salles en France et la convertit en entier.

        Args:
            salles_fr_str (str): Chaîne de caractères représentant le nombre de salles en France

        Returns:
            int: Nombre de salles en France, None si la chaîne n'est pas un nombre valide
        """
        try:
            if pd.isna(salles_fr_str):
                return 'NULL'
            return int(salles_fr_str)
        except ValueError:
            return 'NULL'
    
    @staticmethod
    def clean_duration(duration_str):
        """
        Convertit la durée du film en minutes.

        Args:
            duration_str (str): Format str '1h 30min'

        Returns:
            int: Durée en minutes, None si la chaîne n'est pas dans le format attendu
        """
        # Utilisation d'une expression régulière pour extraire les heures et les minutes
        match = re.search(r'\b(\d+)\s*h(?:ours?)?\s*(\d+)\s*min(?:utes?)?\b', duration_str)
        if match:
            hours, minutes = map(int, match.groups())
            return hours * 60 + minutes
        else:
            return 'NULL'
    
    @staticmethod
    def clean_date(date_str):
        """
        Cleans the 'date_sortie_us' column by extracting the date part and converting it to a datetime object.

        Args:
            date_str (str): The value from the 'date_sortie_us' column.

        Returns:
            datetime: The cleaned date or None if the value is not a valid date.
        """
        try:
            # Extraire la partie de la date et supprimer les caractères indésirables
            date_part = date_str.strip().split()[-1]
            
            # Convertir la date en objet datetime
            cleaned_date = datetime.strptime(date_part, '%d/%m/%Y')
            return f'"{cleaned_date}"'
        except ValueError:
            return 'NULL'
    
    @staticmethod
    def clean_budget(budget):
        """
        Cleans the 'budget' column by removing monetary symbols, spaces, replacing non-numeric entries with 0, and converting to integer.

        Args:
            budget (str): The value from the 'budget' column.

        Returns:
            int: The cleaned budget or 0 if the value is non-numeric.
        """
        # Enlever les symboles monétaires et les espaces
        cleaned_budget = re.sub(r'[\$\€\s]', '', budget)
        
        # Remplacer les entrées non numériques par 0
        cleaned_budget = re.sub(r'[^\d]', '-1', cleaned_budget)
        
        # Conversion en entier
        return int(cleaned_budget)

    @staticmethod
    def extract_pegi_usa_clean(pegi_us):
        """
        Extracts the pattern 'ratifié\s([A-Za-z]+)' from the 'pegi_usa' column.

        Args:
            pegi_usa (str): The value from the 'pegi_usa' column.

        Returns:
            str: The extracted pattern or None if no match is found.
        """
        match = re.search(r'ratifié\s([A-Za-z]+)', pegi_us)
        if match:
            return  f'"{match.group(1)}"'
        else:
            return None
    
    @staticmethod
    def clean_franchise(franchise):
        """
        Nettoie la colonne 'franchise' en vérifiant si chaque entrée est marquée comme 'Franchise'.

        Args:
            franchise (str): Valeur de la colonne 'franchise'

        Returns:
            bool: True si la valeur est 'Franchise', False sinon
        """
        if pd.isna(franchise):
            return False  # Retourne False pour les valeurs NaN
        return franchise.strip().lower() == 'franchise'
        

# Nettoyage du DataFrame
def clean_data(df):
    
    df['entrees_usa'] = df['entrees_usa'].apply(Utils.clean_entrees)
    df['entrees_fr'] = df['entrees_fr'].apply(Utils.clean_entrees)
    df['salles_fr'] = df['salles_fr'].apply(Utils.clean_salles_fr)
    df['duree'] = df['duree'].apply(Utils.clean_duration)
    df['date_sortie_fr'] = df['date_sortie_fr'].apply(Utils.clean_date)
    df['date_sortie_us'] = df['date_sortie_us'].apply(Utils.clean_date)
    df['budget'] = df['budget'].apply(Utils.clean_budget)
    df['pegi_us'] = df['pegi_us'].apply(Utils.extract_pegi_usa_clean)
    df['titre'] = df['titre'].apply(Utils.clean_text)
    df['compositeur'] = df['compositeur'].apply(Utils.clean_text)
    df['genres'] = df['genres'].apply(Utils.clean_text)
    df['pays'] = df['pays'].apply(Utils.clean_text)
    df['pegi_fr'] = df['pegi_fr'].apply(Utils.clean_text)
    df['producteur'] = df['producteur'].apply(Utils.clean_text)
    df['realisateur'] = df['realisateur'].apply(Utils.clean_text)
    df['studio'] = df['studio'].apply(Utils.clean_text)
    df['franchise'] = df['franchise'].apply(Utils.clean_franchise)
    

       

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






# Insertion ou mise à jour des données dans la base de données
def insert_or_update_film(df, conn):
    cursor = conn.cursor()
    for index, row in df.iterrows():
        try:
            titre = row['titre']
            entrees_fr = row['entrees_fr']
            entrees_usa = row['entrees_usa']
            budget = row['budget']
            salles_fr = row['salles_fr']
            date_sortie_fr = row['date_sortie_fr']
            date_sortie_us = row['date_sortie_us']
            duree = row['duree']
            pegi_fr = row['pegi_fr']
            pegi_us = row['pegi_us']
            franchise = row['franchise']
            genres = row['genres']
            pays = row['pays']
            acteurs = row['acteurs']
            producteur = row['producteur']
            realisateur = row['realisateur']
            compositeur = row['compositeur']
            studio = row['studio']

            cursor.execute("SELECT id_film FROM films WHERE titre = %s", (row['titre'],))
            film_result = cursor.fetchone()

            if film_result:
                id_film = film_result[0]
                update_query = """UPDATE films SET entrees_fr=%s, entrees_usa=%s, budget=%s, salles_fr=%s, 
                                  date_sortie_fr=%s, date_sortie_us=%s, duree=%s, pegi_fr=%s, pegi_us=%s, franchise=%s, genres=%s, 
                                  pays=%s, acteurs=%s, producteur=%s, realisateur=%s, compositeur=%s, studio=%s
                                  WHERE id_film=%s"""
                cursor.execute(update_query, tuple(row) + (id_film,))
            else:
                insert_query = f"""INSERT INTO films ('"{titre}"', '"{entrees_fr}"', '"{entrees_usa}"', '"{budget}"', '"{salles_fr}"', 
                                  {date_sortie_fr}, {date_sortie_us}, '"{duree}"', {pegi_fr}, {pegi_us}, {franchise}, '"{genres}"', 
                                  '"{pays}"', '"{acteurs}"', '"{producteur}"', '"{realisateur}"', '"{compositeur}"', '"{studio}"') 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insert_query, tuple(row))

            conn.commit()
        except mysql.connector.Error as e:
            print("Error in Insert/Update:", e)
            conn.rollback()




        
  

# Chargement du CSV, nettoyage et insertion en base de données
def main():
    conn = None
    try:
        data = pd.read_csv('/home/tenshi/projets/Movie_Popularity_Prediction/ml/input_datasets/movies_csv_cleaned.csv')
        data_cleaned = clean_data(data)
        conn = connect_db()
        if conn:
            insert_or_update_film(data_cleaned, conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()