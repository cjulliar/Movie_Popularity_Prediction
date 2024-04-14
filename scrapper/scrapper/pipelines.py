import os
import re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError


class CustomImageNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_urls = item.get('image_urls', [])
        for image_url in image_urls:
            if image_url.startswith('http://') or image_url.startswith('https://'):
                yield Request(image_url, meta={'image_name': item.get('title')})

    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = request.meta.get('image_name', 'default_name').replace('/', '-')
        image_ext = os.path.basename(request.url).split('.')[-1]
        filename = f'{image_name}.{image_ext}'
        return filename

class DataCleaningPipeline:
    def process_item(self, item, spider):
        # Nettoyage des champs textuels
        text_fields = ['realisateur', 'studio', 'titre', 'titre_original', 'nationalite', 
                       'director', 'scenaristes', 'genres', 'langue']
        list_fields = ['acteurs', 'casting_principal', 'casting_complet', 'pays']

        for field in text_fields:
            if field in item and isinstance(item[field], str):
                item[field] = self.clean_text(item[field])

        for field in list_fields:
            if field in item:
                if isinstance(item[field], list):
                    item[field] = ', '.join(map(self.clean_text, item[field]))
                elif isinstance(item[field], str):  # Pour 'casting_complet' qui peut être une chaîne
                    item[field] = self.clean_text(item[field])
                else:
                    spider.logger.warning(f'Field {field} is neither list nor string: {item[field]}')
                    item[field] = ''  # Set to an empty string or handle appropriately


        if 'budget' in item:
            item['budget'] = self.clean_budget(item['budget'])

        if 'date' in item:
            item['date'] = self.clean_date(item['date'])

        if 'popularite_score' in item:
            item['popularite_score'] = item['popularite_score'].replace(',', '')
            item['popularite_score'] = int(item['popularite_score'])

        if 'entrees_premiere_semaine' in item:
            item['entrees_premiere_semaine'] = self.convert_to_float(item['entrees_premiere_semaine'])

        if 'timing' in item:
            item['timing'] = self.convert_timing_to_minutes(item['timing'])

        if 'nombre_vote' in item:
            item['nombre_vote'] = self.clean_and_convert_vote_count(item['nombre_vote'])

        if 'actors' in item:
            item['actors'] = self.clean_actors_names(item['actors'])

        if 'score' in item:
            item['score'] = self.convert_to_float(item['score'])

        if 'genres' in item:
            genres = [genre.strip().lower() for genre in item['genres']]
            item['genres'] = ', '.join(genres)
            item['genres'] = str(item['genres'])

        if 'langue' in item:
            langues = [langue.strip().lower() for langue in item['langue']]
            item['langue'] = ', '.join(langues)
            item['langue'] = str(item['langue'])

        if 'semaine_fr' in item:
            item['semaine_fr'] = self.format_semaine(item['semaine_fr'])

        if 'semaine_usa' in item:
            item['semaine_usa'] = self.format_semaine(item['semaine_usa'])

        if 'entrees_fr' in item:
            item['entrees_fr'] = self.convert_to_float(item['entrees_fr'])

        if 'entrees_usa' in item:
            item['entrees_usa'] = self.convert_to_float(item['entrees_usa'])

        if 'duree' in item:
            item['duree'] = self.convert_duration_to_minutes(str(item['duree']))

        return item

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
        return text.strip().lower()

    def clean_budget(self, budget):
        if isinstance(budget, list):
            budget = budget[0] if budget else '0'
        if not isinstance(budget, str):
            budget = str(budget)
        cleaned_budget = re.sub(r'[\$\¢\£\¥\€\¤\₭\₡\₦\₾\₩\₪\₫\₱\₲\₴\₸\₺\₼\₽\₹]', '', budget).replace(' ', '').replace('?', '').replace('(estimated)', '').replace(',', '').replace('CA', '')
        return cleaned_budget


    def clean_date(self, date_str):
        for date_format in ('%b %d, %Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue
        
        return None

    def convert_to_float(self, str_val):
        return float(str_val.replace(' ', '').replace('k', '000').replace('M', '000000'))

    def convert_timing_to_minutes(self, timing_str):
        match = re.search(r'(?:(\d+)h)?\s*(?:(\d+)min)?', timing_str)
        if not match:
            return timing_str
        hours, minutes = match.groups(default='0')
        return int(hours) * 60 + int(minutes)

    def clean_actors_names(self, actors_list):
        return ','.join(name for name in actors_list if name not in ['avec,'])

    def format_semaine(self, semaine_str):
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

    def convert_duration_to_minutes(self, duration_str):
        if not duration_str:
            return 0
        
        pattern = r'(\d+)h\s*(\d+)m'
        match = re.match(pattern, duration_str)
        if match:
            hours, minutes = map(int, match.groups())
            return hours * 60 + minutes
        else:
            return 0

    def clean_and_convert_vote_count(self, vote_count):
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
            self.conn = mysql.connector.connect(user='tenshi', password='Simplon59', host='casq.mysql.database.azure.com', database='cinema_db')
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
        for field in ['pays', 'genres', 'langue']:
            if field in item and isinstance(item[field], list):
                item[field] = ', '.join(item[field])
                spider.logger.info(f"Champ converti pour {field}: {item[field]}")

        film_id = self.insert_film_data(item, spider)
        if film_id:
            spider.logger.info(f"Film inséré avec l'ID: {film_id}")
            if isinstance(item.get('director', ''), str) and item.get('director', '').strip():
                self.insert_person_data(film_id, item['director'], 'réalisateur', spider)
                spider.logger.info(f"Réalisateur traité: {item['director']}")
            
            if isinstance(item.get('scenaristes', ''), str) and item.get('scenaristes', '').strip():
                self.insert_person_data(film_id, item['scenaristes'], 'scénariste', spider)
                spider.logger.info(f"Scénariste traité: {item['scenaristes']}")

            actors = item.get('actors', [])
            if actors:
                if isinstance(actors, list):
                    for actor in actors:
                        if actor:
                            self.insert_person_data(film_id, actor, 'acteur', spider)
                            spider.logger.info(f"Acteur traité: {actor}")
                else:
                    self.insert_person_data(film_id, actors, 'acteur', spider)
                    spider.logger.info(f"Acteur traité: {actors}")

            casting_complet = item.get('casting_complet', '')
            if casting_complet and isinstance(casting_complet, str):
                for person_name in casting_complet.split(', '):
                    if person_name:
                        self.insert_person_data(film_id, person_name, 'acteur', spider)
                        spider.logger.info(f"Casting complet traité: {person_name}")

        return item

    
    def insert_film_data(self, item, spider):
        
        insert_query = """
            INSERT INTO films (titre, date, budget, genres, pays, nationalite, duree, franchise, remake, popularite_score, score, nombre_vote, semaine_fr, semaine_usa, entrees_fr, entrees_usa, langue, pegi, annee) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            date=VALUES(date), budget=VALUES(budget), genres=VALUES(genres), pays=VALUES(pays),
            nationalite=VALUES(nationalite), duree=VALUES(duree), franchise=VALUES(franchise),
            remake=VALUES(remake), popularite_score=VALUES(popularite_score), score=VALUES(score),
            nombre_vote=VALUES(nombre_vote), semaine_fr=VALUES(semaine_fr), semaine_usa=VALUES(semaine_usa),
            entrees_fr=VALUES(entrees_fr), entrees_usa=VALUES(entrees_usa), langue=VALUES(langue),
            pegi=VALUES(pegi), annee=VALUES(annee);
        """
        try:
            self.cursor.execute(insert_query, (
                item.get('titre'), item.get('date'), item.get('budget'), item.get('genres'),
                item.get('pays'), item.get('nationalite'), item.get('duree'), item.get('franchise'), 
                item.get('remake'), item.get('popularite_score'), item.get('score'), item.get('nombre_vote'), 
                item.get('semaine_fr'), item.get('semaine_usa'), item.get('entrees_fr'), 
                item.get('entrees_usa'), item.get('langue'), item.get('pegi'), item.get('annee')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except MySQLError as e:
            spider.logger.error(f"Erreur lors de l'insertion ou de la mise à jour des données : {e}")
            self.conn.rollback()
            return None
        


    def insert_person_data(self, film_id, person, role, spider):
        # S'assurer que 'person' est une chaîne et qu'elle n'est pas vide
        if isinstance(person, str) and person.strip():
            person_name = person.strip()[:255]  # Nettoyer les espaces et limiter à 255 caractères
        else:
            spider.logger.error(f"Nom de personne invalide (doit être une chaîne non vide): {person}")
            return  # Sortir de la fonction si la condition n'est pas remplie

        try:
            personne_id = self.get_or_create_person_id(person_name, spider)
            if personne_id:
                insert_person_query = """
                    INSERT INTO film_personne (film_id, personne_id, role)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE role=VALUES(role);
                """
                self.cursor.execute(insert_person_query, (film_id, personne_id, role))
                self.conn.commit()
        except MySQLError as e:
            spider.logger.error(f"Erreur lors de l'insertion des données de personnes : {e}")
            self.conn.rollback()





    def get_or_create_person_id(self, person_name, spider):
        if not isinstance(person_name, str):
            spider.logger.error(f"person_name doit être une chaîne de caractères, obtenu {type(person_name)}: {person_name}")
            return None
        try:
            self.cursor.execute("SELECT personne_id FROM personnes WHERE nom = %s", (person_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            self.cursor.execute("INSERT INTO personnes (nom) VALUES (%s)", (person_name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except MySQLError as e:
            spider.logger.error(f"Erreur lors de la récupération ou de la création de l'ID de personne : {e}")
            self.conn.rollback()
            return None
