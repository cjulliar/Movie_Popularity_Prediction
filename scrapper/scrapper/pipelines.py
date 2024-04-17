import os
import re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import datetime
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError



class CustomImageNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_urls = item.get('image_urls', [])
        for image_url in image_urls:
            if image_url.startswith('http://') or image_url.startswith('https://'):
                yield Request(image_url, meta={'image_name': item.get('titre')})

    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = request.meta.get('image_name', 'default_name').replace('/', '-')
        image_ext = os.path.basename(request.url).split('.')[-1]
        filename = f'{image_name}.{image_ext}'
        return filename

class DataCleaningJpBoxPipeline:
    def process_item(self, item, jpspider):
        # Check and clean each item field, using a placeholder if the field is not present
        item['titre'] = UtilsJB.clean_text(item.get('titre', 'NULL'))
        item['realisateur'] = UtilsJB.clean_text(item.get('realisateur', 'NULL'))
        item['pays'] = UtilsJB.clean_text(item.get('pays', 'NULL'))
        item['genres'] = UtilsJB.clean_text(item.get('genres', 'NULL'))
        item['studio'] = UtilsJB.clean_text(item.get('studio', 'NULL'))
        item['franchise'] = UtilsJB.clean_franchise(item.get('franchise', -1))  # Default to -1
        item['entrees_fr'] = UtilsJB.clean_entrees(item.get('entrees_fr', -1))
        item['salle_fr'] = UtilsJB.clean_salles_fr(item.get('salle_fr', -1))
        item['duree'] = UtilsJB.clean_duration(item.get('duree', -1))
        item['date_sortie_fr'] = UtilsJB.clean_date(item.get('date_sortie_fr', 'NULL'))
        item['budget'] = UtilsJB.clean_budget(item.get('budget', -1.1))
        item['pegi_us'] = UtilsJB.extract_pegi_usa_clean(item.get('pegi_us', 'NULL'))
        item['pegi_fr'] = UtilsJB.clean_text(item.get('pegi_fr', 'NULL'))
        item['date_sortie_us'] = UtilsJB.clean_date(item.get('date_sortie_us', 'NULL'))
        item['entrees_usa'] = UtilsJB.clean_entrees(item.get('entrees_usa', -1))
        
        # Handling lists of actors
        actors = item.get('acteurs', ['NULL'])
        item['acteurs'] = [UtilsJB.clean_text(actor) if actor else 'NULL' for actor in actors]

        item['producteur'] = UtilsJB.clean_text(item.get('producteur', 'NULL'))
        item['compositeur'] = UtilsJB.clean_text(item.get('compositeur', 'NULL'))
        
        return item





class UtilsJB:
    @staticmethod
    def clean_text(text):
        if text is None:
            return 'NULL'  # Placeholder for non-scraped string data
        text = re.sub(r'[\"\“\”\‘\’\«\»]', '', text)
        text = text.replace("[", "").replace("]", "").replace("'", "").replace("création", "").replace('#', "")
        return re.sub(r'\s+', ' ', text).strip().lower()

    @staticmethod
    def clean_franchise(franchise):
        if franchise is None:
            return -1  # Return 0 if the input is None
        franchise_str = str(franchise).lower()
        return 1 if 'franchise' in franchise_str else 0

    @staticmethod
    def clean_entrees(entrees_str):
        if isinstance(entrees_str, int):
            return entrees_str
        if entrees_str is None or str(entrees_str).strip() == '':
            return -1  # Return -1 for missing entries
        entrees_str = str(entrees_str).replace(' ', '').replace('$', '')
        try:
            return int(entrees_str.replace(',', ''))
        except ValueError:
            return -1

    @staticmethod
    def extract_pegi_usa_clean(pegi_us):
        if pegi_us is None:
            return 'NULL'  # Placeholder for non-scraped string data
        pegi_us_str = str(pegi_us)
        match = re.search(r'ratifié\s([A-Za-z]+)', pegi_us_str)
        if match:
            return match.group(1)
        else:
            return 'NULL'

    @staticmethod
    def clean_salles_fr(salles_fr_str):
        if salles_fr_str is None:
            return -1  # Return -1 if the input is None
        try:
            return int(salles_fr_str)
        except ValueError:
            return -1

    @staticmethod
    def clean_duration(duration_str):
        if duration_str is None:
            return -1  # Return -1 if the input is None
        duration_str = str(duration_str)
        match = re.search(r'\b(\d+)\s*h(?:ours?)?\s*(\d+)\s*min(?:utes?)?\b', duration_str)
        if match:
            hours, minutes = map(int, match.groups())
            return hours * 60 + minutes
        return -1

    @staticmethod
    def clean_date(date_str):
        if date_str is None or not date_str.strip():
            return 'NULL'
        try:
            date_part = date_str.strip().split()[-1]
            cleaned_date = datetime.datetime.strptime(date_part, '%d/%m/%Y')
            return cleaned_date.strftime('%Y-%m-%d')
        except ValueError:
            return 'NULL'

    @staticmethod
    def clean_budget(budget):
        if budget is None:
            return -1.1  # Return 0.0 if the input is None
        budget_str = str(budget)
        budget_str = re.sub(r'[^\d.]', '', budget_str)
        return float(budget_str) if budget_str else -1.1



class DataCleaningImdbPipeline:
    def process_item(self, item, semaine):
        # Nettoyage des champs textuels
        text_fields = [ 'studio', 'titre'
                    , 'genres']
        list_fields = ['pays']

        for field in text_fields:
            if field in item and isinstance(item[field], str):
                item[field] = Utils.clean_text(item[field])

        for field in list_fields:
            if field in item:
                if isinstance(item[field], list):
                    # Vérifie si le premier élément est 'avec' ou 'Avec' et le supprime si nécessaire
                    if item[field] and item[field][0].lower() == 'avec':
                        item[field].pop(0)
                    # Nettoyage du reste de la liste
                    item[field] = ', '.join(map(Utils.clean_text, item[field]))
                elif isinstance(item[field], str):  # Pour 'casting_complet' qui peut être une chaîne
                    item[field] = Utils.clean_text(item[field])
                else:
                    semaine.logger.warning(f'Field {field} is neither list nor string: {item[field]}')
                    item[field] = ''  # Set to an empty string or handle appropriately

    


        if 'budget' in item:
            item['budget'] = Utils.clean_budget(item['budget'])

        if 'semaine_fr' in item:
            item['semaine_fr'] = Utils.clean_date(item['semaine_fr'])

        
        if 'genres' in item:
            genres = [genre.strip().lower() for genre in item['genres']]
            item['genres'] = ', '.join(genres)
            item['genres'] = str(item['genres'])

                

        if 'entrees_fr' in item:
            item['entrees_fr'] = Utils.convert_to_float(item['entrees_fr'])

        
        if 'duree' in item:
            item['duree'] = Utils.convert_duration_to_minutes(item['duree'])

        return item

    

class Utils:
    @staticmethod
    def format_semaine(semaine_str):
        months = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        match = re.search(r'(\d+)\sau\s(\d+)\s(\w+)\s(\d+)', semaine_str)
        if not match:
            return semaine_str
        start_day, end_day, month_word, year = match.groups()
        month = months.get(month_word.lower(), '01')
        start_date_str = f"{start_day}/{month}/{year}"
        end_date_str = f"{end_day}/{month}/{year}"
        return f"{start_date_str} au {end_date_str}"
    
    @staticmethod
    def convert_duration_to_minutes(duration_str):
        if not duration_str.strip():  # Nettoyer les espaces avant et après
            return 0
        
        # Utiliser strip() pour nettoyer les espaces blancs autour de la chaîne si nécessaire
        pattern = r'(\d+)\s*h\s*(\d+)\s*m'
        match = re.search(pattern, duration_str.strip())
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            return hours * 60 + minutes
        else:
            print(f"Failed to parse duration: '{duration_str}'")
            return 0
    
    @staticmethod
    def clean_and_convert_vote_count(vote_count):
        if not vote_count:
            return None 
        
        if 'K' in vote_count:
            vote_count = vote_count.replace('K', '')
            count = float(vote_count) * 1000
        elif 'M' in vote_count:
            vote_count = vote_count.replace('M', '')
            count = float(vote_count) * 1000000
        else:
            try:
                count = float(vote_count)
            except ValueError:
                return None  
        return int(count)

    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
        return text.strip().lower()

    @staticmethod
    def clean_budget(budget):
        if isinstance(budget, list):
            budget = budget[0] if budget else '0'
        if not isinstance(budget, str):
            budget = str(budget)
        cleaned_budget = re.sub(r'[\$\¢\£\¥\€\¤\₭\₡\₦\₾\₩\₪\₫\₱\₲\₴\₸\₺\₼\₽\₹]', '', budget).replace(' ', '').replace('?', '').replace('(estimated)', '').replace(',', '').replace('CA', '')
        return cleaned_budget


    @staticmethod
    def clean_date(date_str):
        try:
            # Convertissez la date en format 'YYYY-MM-DD'
            date_object = datetime.strptime(date_str, '%b %d, %Y')
            return date_object.strftime('%Y-%m-%d')
        except ValueError:
            # Si une erreur survient, retournez None ou gérez l'erreur comme vous le souhaitez
            return None


    @staticmethod
    def convert_to_float(str_val):
        return float(str_val.replace(' ', '').replace('k', '000').replace('M', '000000'))


    @staticmethod
    def convert_timing_to_minutes(timing_str):
        match = re.search(r'(?:(\d+)h)?\s*(?:(\d+)min)?', timing_str)
        if not match:
            return timing_str
        hours, minutes = match.groups(default='0')
        return int(hours) * 60 + int(minutes)


    
    
    @staticmethod
    def clean_and_convert_vote_count(vote_count):
        if not vote_count:
            return None 
        
        if 'K' in vote_count:
            vote_count = vote_count.replace('K', '')
            count = float(vote_count) * 1000
        elif 'M' in vote_count:
            vote_count = vote_count.replace('M', '')
            count = float(vote_count) * 1000000
        else:
            try:
                count = float(vote_count)
            except ValueError:
                return None  
        return int(count)



class MySQLStorePipeline(object):
    def open_spider(self, spider):
        try:
            self.conn = mysql.connector.connect(user='tenshi', password='Simplon59', host='casq.mysql.database.azure.com', database='db_movies')
            self.cursor = self.conn.cursor()
        except MySQLError as e :
            spider.logger.error(f"Erreur de connexion à la base de données : {e}")
            raise

    
    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            try:
                self.conn.close()
            except MySQLError as e :
                spider.logger.error(f"Erreur lors de la fermeture de la connexion à la base de données : {e}")

    
    def process_item(self, item, spider):
        # Convertir les champs de liste en chaînes avant l'insertion
        for field in ['pays', 'genres']:
            if field in item and isinstance(item[field], list):
                item[field] = ', '.join(item[field])
                spider.logger.info(f"Champ converti pour {field}: {item[field]}")
        
        if 'casting_complet' in item and isinstance(item['casting_complet'], list):
            item['acteurs'] = ', '.join(item['casting_complet'])
        

        

           

        return item

    
    def insert_film_data(self, item, spider):
        
        insert_query = """
            INSERT INTO films (titre, acteurs, budget, compositeur, semaine_fr,semaine_usa, duree, entrees_fr, franchise, genres, pays, pegi_fr, producteur, realisateur, salles_fr, entrees_usa, studio) 
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            date=VALUES(date),acteurs=VALUES(acteurs), budget=VALUES(budget), genres=VALUES(genres), pays=VALUES(pays),
            duree=VALUES(duree), franchise=VALUES(franchise), semaine_fr=VALUES(semaine_fr),
            semaine_usa=VALUES(semaine_usa), entrees_fr=VALUES(entrees_fr), entrees_usa=VALUES(entrees_usa),
            annee=VALUES(annee), pegi_fr=VALUES(pegi_fr), pegi_usa=VALUES(pegi_usa),
            salles_fr=VALUES(salles_fr), studio=VALUES(studio); 
        """
        try:
            self.cursor.execute(insert_query, (
                item.get('titre'), item.get('acteurs'), item.get('budget'), item.get('compositeur'),
                item.get('semaine_fr'), item.get('semaine_usa'), item.get('duree'), 
                item.get('entress_fr'), item.get('franchise'), item.get('genres'), item.get('pays'), 
                item.get('pegi_fr'), item.get('pegi_usa'), item.get('producteur'), item.get('realisateur'), item.get('entrees_usa'), item.get('salles_fr'), item.get('studio')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except MySQLError as e:
            spider.logger.error(f"Erreur lors de l'insertion ou de la mise à jour des données : {e}")
            self.conn.rollback()
            return None
        


