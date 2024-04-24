import os
import re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import datetime
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError
import locale


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

'''class DataCleaningJpBoxPipeline:
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
        
        if 'duree' in item:
            item['duree'] = self.convert_duration_to_minutes(str(item['duree']))


        return item

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
        return text.strip().lower()

    def clean_budget(self, budget):
        if isinstance(budget, list):
            budget = budget[0] if budget else '0'
        cleaned_budget = re.sub(r'[\$\¢\£\¥\€\¤\₭\₡\₦\₾\₩\₪\₫\₱\₲\₴\₸\₺\₼\₽\₹]', '', budget).replace(' ', '').replace('?', '').replace('(estimated)', '').replace(',', '')
        return cleaned_budget'''



'''class UtilsJB:
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
    def clean_and_format_date(date_str):
            # Configure le paramètre régional pour interpréter le mois en français
        locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')  # Assurez-vous que cette locale est supportée par votre système

        # Convertit la chaîne de caractères en un objet date
        date_object = datetime.strptime(date_str, "%d %b. %Y")
        return date_object

    @staticmethod
    def clean_budget(budget):
        if budget is None:
            return -1.1  # Return 0.0 if the input is None
        budget_str = str(budget)
        budget_str = re.sub(r'[^\d.]', '', budget_str)
        return float(budget_str) if budget_str else -1.1'''



class DataCleaningImdbPipeline:
    def process_item(self, item, spider):
        # Nettoyage des champs textuels
        text_fields = [ 'studio', 'titre'
                    , 'genres', 'producteur']
        

        for field in text_fields:
            if field in item and isinstance(item[field], str):
                item[field] = Utils.clean_text(item[field])

        
        # Nettoyage du casting complet
        if 'casting_complet' in item:
            if isinstance(item['casting_complet'], list):
                # Supposant que c'est déjà une liste de noms
                casting_complet = [actor.strip().lower() for actor in item['casting_complet']]
            item['casting_complet'] = ', '.join(casting_complet)

        

        
        if 'pays' in item:
            if isinstance(item['pays'], list):
                # Supposant que c'est déjà une liste de noms
                pays = [itempays.strip().lower() for itempays in item['pays']]
            item['pays'] = ', '.join(pays)

        
    
        if 'image_url' in item:
            item['image_url']

        if 'budget_allo' in item:
            item['budget_allo'] = Utils.clean_budget(item['budget_allo'])

        if 'semaine_fr' in item:
            item['semaine_fr'] = Utils.clean_and_format_date(item['semaine_fr'])

        if 'genres' in item:
            if isinstance(item['genres'], list):
                # Supposant que c'est déjà une liste de noms
                genres = [genre.strip().lower() for genre in item['genres']]
            item['genres'] = ', '.join(genres)

        if 'studio' in item:
            if isinstance(item['studio'], list):
                # Supposant que c'est déjà une liste de noms
                studio = [studioitem.strip().lower() for studioitem in item['studio']]
            item['studio'] = ', '.join(studio)

        
            

        if 'entrees_fr' in item:
            item['entrees_fr'] = Utils.clean_date(item['entrees_fr'])
            
        if 'duree_allo' in item:
            item['duree_allo'] = Utils.clean_duration(item['duree_allo'])
        
        if 'duree' in item:
            item['duree'] = Utils.convert_duration_to_minutes(item['duree'])
        
        if 'realisateur_allo' in item and item['realisateur_allo']:
            # Assurez-vous qu'il y a au moins un élément dans la liste avant d'essayer d'accéder au dernier
            item['realisateur_allo'] = item['realisateur_allo'][-1].lower()
        else:
            # Gérez le cas où 'realisateur_allo' n'existe pas ou est une liste vide
            item['realisateur_allo'] = None
            spider.logger.warning("List 'realisateur_allo' is empty or does not exist for item: {}".format(item))

        
        if 'semaine_fr_allo' in item:
            item['semaine_fr_allo'] = Utils.convert_date_fr_from_allo(item['semaine_fr_allo'])
        
        if 'pegi_fr_allo' in item and item['pegi_fr_allo'] is not None:
            item['pegi_fr_allo'] = item['pegi_fr_allo'].lower()
        else:
            item['pegi_fr_allo'] = None
        
        if 'pays_allo' in item:
            item['pays_allo'] = item['pays_allo'].lower()

        if 'entrees_fr_allo' in item:
            item['entrees_fr_allo'] = item['entrees_fr_allo']

        if 'studio_allo' in item and item['studio_allo'] is not None:
            item['studio_allo'] = item['studio_allo'].lower()
        else:
            item['studio_allo'] = None

        if 'salles_fr_allo' in item and isinstance(item['salles_fr_allo'], str):
            seances_match = re.search(r'\(([\d\s\u202F]+)\)', item['salles_fr_allo'])
            if seances_match:
                clean_number = seances_match.group(1).replace('\u202F', '')
                item['salles_fr_allo'] = int(clean_number)
        else:
            # Loguer un avertissement ou définir une valeur par défaut si nécessaire
            spider.logger.warning(f"'salles_fr_allo' is missing or not a string for item {item.get('titre', 'Unknown title')}")
            item['salles_fr_allo'] = None


        

        if 'casting_complet_allo' in item:
            if item['casting_complet_allo']:
                # Vérifie si 'casting_complet_allo' est une liste
                if isinstance(item['casting_complet_allo'], list):
                    # Traite chaque élément de la liste
                    casting_complet_allo = [acteur.replace('Avec', '').strip().lower() for acteur in item['casting_complet_allo'] if acteur.strip()]
                else:
                    # Traite le cas où 'casting_complet_allo' serait un string unique (peu probable mais couvert)
                    casting_complet_allo = [item['casting_complet_allo'].replace('Avec', '').strip().lower()]

                # Supprime le premier élément si la liste n'est pas vide après traitement
                if casting_complet_allo:
                    item['casting_complet_allo'] = ', '.join(casting_complet_allo[1:])
                else:
                    item['casting_complet_allo'] = None
            else:
                item['casting_complet_allo'] = None


        producteur_allo = item.get('producteur_allo')
        if isinstance(producteur_allo, list) and len(producteur_allo) > 1:
            item['producteur_allo'] = producteur_allo[1].lower()
        elif isinstance(producteur_allo, str):
            item['producteur_allo'] = producteur_allo.lower()
        else:
            item['producteur_allo'] = None

        

        if 'genres_allo' in item:
            if isinstance(item['genres_allo'], list):  # Ensure it is a list
                # Slice if necessary and remove any '|' and strip spaces
                genres_to_process = item['genres_allo'][3:] if len(item['genres_allo']) >= 3 else item['genres_allo']
                item['genres_allo'] = [genre.replace('|', '').strip().lower() for genre in genres_to_process if genre.strip()]
                item['genres_allo'] = item['genres_allo'].pop()
        
        if 'entrees_fr_allo' in item:
            item['entrees_fr_allo'] = item['entrees_fr_allo']
        
        if 'semaine_usa_allo' in item:
            item['semaine_usa_allo'] = Utils.parse_french_date(item['semaine_usa_allo'])
        
        if 'entrees_usa_allo' in item:
            item['entrees_usa_allo'] = item['entrees_usa_allo']
   
        return item
    
        

    

class Utils:

    @staticmethod
    def parse_french_date(date_str):
        # Dictionnaire pour convertir les mois français en numéro de mois
        months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        
        # Extraction des composants de la date
        parts = date_str.split()
        day = parts[0]  # Jour initial ("05" de "05 au 8 avril 2024")
        month_name = parts[3]  # Nom du mois ("avril")
        year = parts[4]  # Année ("2024")

        # Conversion du mois en numéro
        month = months[month_name]

        # Création de l'objet date
        formatted_date = datetime(int(year), month, int(day)).strftime('%Y-%m-%d')
        
        return formatted_date
    @staticmethod
    def clean_and_format_date(date_str):
        # Dictionnaire pour convertir le mois français en nombre
        months = {
            'janv.': '01', 'févr.': '02', 'mars': '03', 'avr.': '04',
            'mai': '05', 'juin': '06', 'juil.': '07', 'août': '08',
            'sept.': '09', 'oct.': '10', 'nov.': '11', 'déc.': '12'
        }

        # Extraction des composants de la date
        day, month_abbr, year = date_str.split()

        # Remplacement du mois abrégé par son numéro correspondant
        month = months[month_abbr]

        # Construction de la nouvelle chaîne de date en format ISO
        iso_date_string = f"{year}-{month}-{day.zfill(2)}"  # Ajoute un zéro à gauche pour les jours de 1 à 9

        # Conversion en objet datetime
        date_object = datetime.strptime(iso_date_string, "%Y-%m-%d")

        # Retourne uniquement la partie date de l'objet datetime
        return date_object.date()
    

    @staticmethod
    def convert_date_fr_from_allo(date_str):
        # Dictionnaire pour la conversion des mois
        months = {
            "janvier": "01", "février": "02", "mars": "03", "avril": "04",
            "mai": "05", "juin": "06", "juillet": "07", "août": "08",
            "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
        }

        if date_str:  # Vérifiez si la chaîne n'est pas None ou vide
            parts = date_str.strip().split()
            if len(parts) == 3:
                day, month, year = parts
                # Assurez-vous que les variables sont convertibles en entiers
                try:
                    day = int(day)
                    year = int(year)
                    month = months.get(month.lower(), None)  # Convertissez le mois en nombre
                    if month is not None:
                        return f"{year}-{month}-{day:02d}"  # Formatez la date
                    else:
                        return None  # Retournez None si le mois n'est pas valide
                except ValueError:
                    return None  # Retournez None si la conversion en entier échoue
            else:
                return None  # Retournez None si les parties ne sont pas trois
        else:
            return None  # Retournez None si la chaîne est vide ou None

   

    
    @staticmethod
    def convert_duration_to_minutes(duration_str):
        if not duration_str.strip():  # Nettoyer les espaces avant et après
            return None
        
        # Utiliser strip() pour nettoyer les espaces blancs autour de la chaîne si nécessaire
        pattern = r'(\d+)\s*h\s*(\d+)\s*m'
        match = re.search(pattern, duration_str.strip())
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            return hours * 60 + minutes
        else:
            print(f"Failed to parse duration: '{duration_str}'")
            return None
    
    

    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
        return text.strip().lower()
    
    @staticmethod
    def clean_budget(budget):
        if isinstance(budget, list):
            budget = budget[0] if budget else 'NULL'
        if not isinstance(budget, str):
            budget = str(budget)
        # Remove currency symbols and unwanted characters, then strip any whitespace
        cleaned_budget = re.sub(r'[\$\¢\£\¥\€\¤\₭\₡\₦\₾\₩\₪\₫\₱\₲\₴\₸\₺\₼\₽\₹]', '', budget)
        cleaned_budget = re.sub(r'[?.,\sCA(estimé)US]', '', cleaned_budget)
        # Convert the cleaned budget to an integer
        try:
            return int(cleaned_budget)
        except ValueError:
            # In case the conversion fails, likely due to empty string or invalid format
            return None


    @staticmethod
    def clean_duration(duration_list):
        # Ensure the input is a list, if not, handle it appropriately
        if not isinstance(duration_list, list):
            if isinstance(duration_list, str):
                duration_list = [duration_list]  # Make it a list if it's a single string
            else:
                return None  # Return None if it's neither a list nor a string
        
        # Join the list into a single string
        duration_str = ''.join(duration_list)
        
        # Use regular expression to find the duration pattern 'Xh Ymin'
        match = re.search(r'(\d+)h (\d+)min', duration_str)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            # Convert hours to minutes and add to minutes
            total_minutes = hours * 60 + minutes
            return total_minutes
        else:
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


    
    
    


class MySQLStoreSemainePipeline(object):
    def open_spider(self, semaine):
        try:
            self.conn = mysql.connector.connect(user='tenshi', password='Simplon59', host='casq.mysql.database.azure.com', database='db_movies')
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            semaine.logger.error(f"Erreur de connexion à la base de données : {e}")
            raise

    def close_spider(self, semaine):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            try:
                self.conn.close()
            except mysql.connector.Error as e:
                semaine.logger.error(f"Erreur lors de la fermeture de la connexion à la base de données : {e}")

    def process_item(self, item, semaine):
        
        add_movie = ("""INSERT INTO test
                (titre, acteurs,budget, genres, pays, duree, semaine_fr, semaine_usa, producteur, realisateur, entrees_usa, studio, images, synopsis, pegi_fr, salles_fr, entrees_fr) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")


        # Prepare data for insertion
        data_movie = (
            item.get('titre', None),
            item.get('casting_complet_allo', None),
            item.get('budget_allo', None),
            item.get('genres_allo', None),
            item.get('pays_allo', None),
            item.get('duree_allo', None),
            item.get('semaine_fr_allo', None),
            item.get('semaine_usa_allo', None),
            item.get('producteur_allo', None),        
            item.get('realisateur_allo', None),
            item.get('entrees_usa_allo', None),
            item.get('studio_allo', None),
            item.get('image_url', None),
            item.get('synopsis', None),
            item.get('pegi_fr_allo', None),
            item.get('salles_fr_allo', None),
            item.get('entrees_fr_allo', None),
            
            
        )
                    


        data_movie = tuple(None if isinstance(value, str) and not value.strip() else value 
                       for value in data_movie)

        try:
            self.cursor.execute(add_movie, data_movie)
            self.conn.commit()
        except mysql.connector.Error as err:
            semaine.logger.error(f"Erreur SQL : {err.msg}")
            self.conn.rollback()  # Effectuer un rollback en cas d'échec de l'insertion
        return item




class MySQLStoreSemaineProchainePipeline(object):
    def open_spider(self, semaine_prochaine):
        try:
            self.conn = mysql.connector.connect(user='tenshi', password='Simplon59', host='casq.mysql.database.azure.com', database='db_movies')
            self.cursor = self.conn.cursor()
            self.clear_table()
        except mysql.connector.Error as e:
            semaine_prochaine.logger.error(f"Erreur de connexion à la base de données : {e}")
            raise

    def close_spider(self, semaine_prochaine):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            try:
                self.conn.close()
            except mysql.connector.Error as e:
                semaine_prochaine.logger.error(f"Erreur lors de la fermeture de la connexion à la base de données : {e}")

    def clear_table(self):
        # Effacer toutes les données de la table avant de commencer les insertions
        try:
            self.cursor.execute("DELETE FROM predict_films")
            self.conn.commit()
        except mysql.connector.Error as err:
            print("Error occurred: {}".format(err))
            self.conn.rollback()
            
    def process_item(self, item, semaine_prochaine):

        
        add_movie = ("""INSERT INTO predict_films
                (titre, acteurs,budget, genres, pays, duree, semaine_fr, semaine_usa, producteur, realisateur, entrees_usa, studio, images, synopsis, pegi_fr, salles_fr, entrees_fr) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")


        # Prepare data for insertion
        data_movie = (
            item.get('titre', None),
            item.get('casting_complet_allo', None),
            item.get('budget_allo', None),
            item.get('genres_allo', None),
            item.get('pays_allo', None),
            item.get('duree_allo', None),
            item.get('semaine_fr_allo', None),
            item.get('semaine_usa_allo', None),
            item.get('producteur_allo', None),        
            item.get('realisateur_allo', None),
            item.get('entrees_usa_allo', None),
            item.get('studio_allo', None),
            item.get('image_url', None),
            item.get('synopsis', None),
            item.get('pegi_fr_allo', None),
            item.get('salles_fr_allo', None),
            item.get('entrees_fr_allo', None),
            
            
        )
            

       
                    


        data_movie = tuple(None if isinstance(value, str) and not value.strip() else value 
                       for value in data_movie)

        try:
            self.cursor.execute(add_movie, data_movie)
            self.conn.commit()
        except mysql.connector.Error as err:
            semaine_prochaine.logger.error(f"Erreur SQL : {err.msg}")
            self.conn.rollback()  # Effectuer un rollback en cas d'échec de l'insertion
        return item

   