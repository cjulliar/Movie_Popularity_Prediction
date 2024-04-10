from itemadapter import ItemAdapter
import os, re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from datetime import datetime


# Classe de pipeline personnalisée pour le traitement des images
class CustomImageNamePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        # Génère des requêtes de téléchargement pour chaque URL d'image trouvée
        image_urls = item.get('image_urls', [])
        for image_url in image_urls:
            # Assurez-vous que l'URL commence par http:// ou https:// avant de yield la requête
            if image_url.startswith('http://') or image_url.startswith('https://'):
                yield Request(image_url, meta={'image_name': item.get('title')})
            # Si vous décidez de ne pas logger, assurez-vous quand même que l'URL est valide
            # Sinon, l'URL invalide sera simplement ignorée

    def file_path(self, request, response=None, info=None, *, item=None):
        # Définit le chemin de fichier où l'image sera sauvegardée
        image_name = request.meta.get('image_name', 'default_name').replace('/', '-')
        image_ext = os.path.basename(request.url).split('.')[-1]
        # Formatte le nom de fichier de l'image
        filename = f'{image_name}.{image_ext}'
        return filename



class DataCleaningPipeline:
    def process_item(self, item, spider):

        # Nettoye le champ title
        if item.get('title'):
            item['title'] = item['title'].strip()

        #Nettoye et converti le champ timing
        if item.get('timing'):
            item['timing'] = self.convert_timing_to_minutes(item['timing'])
           

        # Nettoye le champ director
        if item.get('director'):
            item['director'] = self.clean_director_names(item['director'])
           
        
        # Nettoye l'annee
        if item.get('annee'):
            item['annee'] = int(item['annee'].strip())

        
        # Nettoye le popularite_score
        if item.get('popularite_score'):
            item['popularite_score'] = int(item['popularite_score'].strip())


        # Nettoye le champ actors
        if item.get('actors'):
            item['actors'] = self.clean_actors_names(item['actors'])

        # Nettoye le champ score 
        if item.get('score'):
            item['score'] = int(item['score'])
           
        # Nettoye le champ genres
        if item.get('genres'):
            item['genres'] = item['genres'].strip().lower()

        # Nettoye le champ nationalite
        if item.get('nationalite'):
            item['nationalite'] = item['nationalite'].strip().lower()

        # Nettoye le champ studio
        if item.get('studio'):
            item['studio']= item['studio'].strip().lower()

        # Nettoye le champ titre_original
        if item.get('titre_original'):
           item['titre_original'] = item['titre_original'].strip().lower()

        # Nettoye le champ semaine_fr
        if 'semaine_fr' in item:
            item['semaine_fr'] = self.format_semaine_fr(item['semaine_fr'])
           
        
        # Nettoye le champ semaine_usa
        if 'semaine_usa' in item:
            item['semaine_usa'] = self.format_semaine_usa(item['semaine_usa'])
           
        
        # Nettoye le champ entrees_fr
        if item.get('entrees_fr'):
            item['entrees_fr'] = int(item['entrees_fr'].replace(" ", ""))
           
        
        # Nettoye le champ entrees_usa
        if item.get('entrees_usa'):
            item['entrees_usa'] = int(item['entrees_usa'].replace(" ", ""))
        
        return item
    
    def convert_timing_to_minutes(self, timing_str):
        # Cherche des heures et des minutes dans la str
        match = re.search(r'(?:(\d+)h)?\s*(?:(\d+)min)?', timing_str)
        if not match:
            return timing_str
        
        heures, minutes = match.groups()
        total_minutes = 0

        if minutes:
            total_minutes += int(minutes)
        
        return total_minutes



    def clean_director_names(self, directors_list):
        return ','.join(name for name in directors_list if name not in ['De', 'Par'])
    
    
    
    def format_semaine_fr(self, semaine_fr_str):
        # Définition des mois pour la conversion
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }

        # Expression régulière ajustée pour capturer les dates s'étendant sur deux mois
        match = re.search(r'(\d+)\s(\w+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_fr_str)
        if not match:
            # Essayez un autre pattern si le premier échoue (pour gérer le cas d'un seul mois)
            match = re.search(r'(\d+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_fr_str)
            if not match:
                return semaine_fr_str  # Retourner la chaîne originale si aucun pattern ne correspond

        if len(match.groups()) == 5:
            # Cas où la plage de dates s'étend sur deux mois différents
            start_day, start_month_word, end_day, end_month_word, year = match.groups()
        else:
            # Cas où la plage de dates est dans le même mois
            start_day, end_day, month_word, year = match.groups()
            start_month_word = end_month_word = month_word

        start_month = months.get(start_month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        end_month = months.get(end_month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        
        # Convertir en format désiré
        start_date_str = f"{start_day}/{start_month}/{year}"
        end_date_str = f"{end_day}/{end_month}/{year}"
        formatted_semaine_fr = f"{start_date_str} au {end_date_str}"

        return formatted_semaine_fr
    
    def format_semaine_usa(self, semaine_usa_str):
        # Définition des mois pour la conversion
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }

        # Expression régulière ajustée pour capturer les dates s'étendant sur deux mois
        match = re.search(r'(\d+)\s(\w+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_usa_str)
        if not match:
            # Essayez un autre pattern si le premier échoue (pour gérer le cas d'un seul mois)
            match = re.search(r'(\d+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_usa_str)
            if not match:
                return semaine_usa_str  # Retourner la chaîne originale si aucun pattern ne correspond

        if len(match.groups()) == 5:
            # Cas où la plage de dates s'étend sur deux mois différents
            start_day, start_month_word, end_day, end_month_word, year = match.groups()
        else:
            # Cas où la plage de dates est dans le même mois
            start_day, end_day, month_word, year = match.groups()
            start_month_word = end_month_word = month_word

        start_month = months.get(start_month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        end_month = months.get(end_month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        
        # Convertir en format désiré
        start_date_str = f"{start_day}/{start_month}/{year}"
        end_date_str = f"{end_day}/{end_month}/{year}"
        formatted_semaine_usa = f"{start_date_str} au {end_date_str}"

        return formatted_semaine_usa



    def clean_director_names(self, directors_list):
        return ','.join(name for name in directors_list if name not in ['De', 'Par'])
    
    def clean_actors_names(self, actors_list):
        return ','.join(name for name in actors_list if name not in ['avec,'])
    
    def format_semaine_fr(self, semaine_fr_str):
        # Remplacer les noms de mois par leur numéro équivalent pour faciliter la conversion
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
        # Extraire les composants de la date
        match = re.search(r'(\d+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_fr_str)
        if not match:
            return semaine_fr_str  # Retourner la chaîne originale si le format ne correspond pas

        start_day, end_day, month_word, year = match.groups()
        month = months.get(month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        
        # Convertir en format désiré
        start_date_str = f"{start_day}/{month}/{year}"
        end_date_str = f"{end_day}/{month}/{year}"
        formatted_semaine_fr = f"{start_date_str} au {end_date_str}"

        return formatted_semaine_fr
    
    def format_semaine_usa(self, semaine_usa_str):
        # Remplacer les noms de mois par leur numéro équivalent pour faciliter la conversion
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
        # Extraire les composants de la date
        match = re.search(r'(\d+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_usa_str)
        if not match:
            return semaine_usa_str  # Retourner la chaîne originale si le format ne correspond pas

        start_day, end_day, month_word, year = match.groups()
        month = months.get(month_word.lower(), '01')  # Utiliser '01' comme valeur par défaut
        
        # Convertir en format désiré
        start_date_str = f"{start_day}/{month}/{year}"
        end_date_str = f"{end_day}/{month}/{year}"
        formatted_semaine_usa = f"{start_date_str} au {end_date_str}"

        return formatted_semaine_usa
    
    def convert_to_int(self, score):
        # Normalise la chaîne de caractères : supprime les espaces et remplace les virgules par des points
        score = score.replace(' ', '').replace(',', '.')
        
        # Convertit les abréviations en nombres entiers
        if 'k' in score:
            # Retire le 'k' et multiplie par 1000
            return float((score.replace('k', '')) * 1000)
        elif 'M' in score:
            # Retire le 'M' et multiplie par 1 million
            return float((score.replace('M', '')) * 1000000)
        else:
            # Si aucun des cas ci-dessus, tente simplement de convertir en int
            return float(score)
            







    