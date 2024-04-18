import pandas as pd
import re
from datetime import datetime

class Utils:
    @staticmethod
    def clean_text(text):
        if pd.isna(text):
            return ''
        # Utiliser re.sub() pour enlever tous les types de guillemets
        text = re.sub(r'[\"\“\”\‘\’\«\»]', '', text)
        # Supprimer les autres caractères indésirables
        text = text.replace("[", "").replace("]", "").replace("'", "").replace("création", "").replace('#', "")
        # Supprimer les espaces superflus et mettre le texte en minuscule
        return re.sub(r'\s+', ' ', text).strip().lower()



    @staticmethod
    def clean_entrees(entrees_str):
        if isinstance(entrees_str, int):
            return entrees_str
        if entrees_str is None or str(entrees_str).strip() == '':
            return 0
        entrees_str = str(entrees_str).replace(' ', '').replace('$', '')
        try:
            return int(entrees_str.replace(',', ''))
        except ValueError:
            return 0


    @staticmethod
    def clean_salles_fr(salles_fr_str):
        if pd.isna(salles_fr_str):
            return 0
        try:
            return int(salles_fr_str)
        except ValueError:
            return 0

    @staticmethod
    def clean_duration(duration_str):
        if pd.isna(duration_str):
            return 0
        match = re.search(r'\b(\d+)\s*h(?:ours?)?\s*(\d+)\s*min(?:utes?)?\b', duration_str)
        if match:
            hours, minutes = map(int, match.groups())
            return hours * 60 + minutes
        return 0

    @staticmethod
    def clean_date(date_str):
        if pd.isna(date_str) or not date_str.strip():
            return '0000-00-00'
        try:
            date_part = date_str.strip().split()[-1]
            cleaned_date = datetime.strptime(date_part, '%d/%m/%Y')
            return cleaned_date.strftime('%Y-%m-%d')
        except ValueError:
            return '0000-00-00'

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

# Charger le fichier CSV
data = pd.read_csv('ml/input_datasets/test/movies_csv_cleaned.csv')

# Appliquer les fonctions de nettoyage
for col in data.columns:
    if data[col].dtype == object:
        data[col] = data[col].apply(Utils.clean_text)
    elif col in ['entrees_fr', 'entrees_usa', 'salles_fr']:
        data[col] = data[col].apply(Utils.clean_entrees)
    elif col in ['budget']:
        data[col] = data[col].apply(Utils.clean_budget)
    elif col in ['date_sortie_fr', 'date_sortie_us']:
        data[col] = data[col].apply(Utils.clean_date)
    elif col in ['duree']:
        data[col] = data[col].apply(Utils.clean_duration)

# Sauvegarder le fichier nettoyé
data.to_csv('ml/input_datasets/test/test.csv', index=False)

print("Le nettoyage est terminé et le fichier a été sauvegardé.")
