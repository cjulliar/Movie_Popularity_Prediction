import os
import re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from datetime import datetime

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
        text_fields = ['acteurs', 'realisateur', 'studio', 'titre', 'titre_original', 'nationalite', 'casting_principal', 'director', 'casting_complet', 'scenaristes', 'pays']
        for field in text_fields:
            if field in item:
                # Vérifier si le champ est une liste
                if isinstance(item[field], list):
                    # Nettoyer chaque élément de la liste en utilisant la fonction clean_text
                    item[field] = [self.clean_text(str(text)) for text in item[field]]
                else:
                    # Appliquer la fonction clean_text au champ
                    item[field] = self.clean_text(str(item[field]))

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
         
        if 'nbre_vote' in item:
            item['nbre_vote'] = self.clean_and_convert_vote_count(item['nbre_vote'])
          

        if 'actors' in item:
            item['actors'] = self.clean_actors_names(item['actors'])

        if 'score' in item:
            item['score'] = self.convert_to_float(item['score'])

        if 'genres' in item:
            genres = [genre.strip().lower() for genre in item['genres']]
            item['genres'] = ', '.join(genres)

        if 'langue' in item:
            langues = [langue.strip().lower() for langue in item['langue']]
            item['langue'] = ', '.join(langues)

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
        cleaned_budget = re.sub(r'[\$\¢\£\¥\€\¤\₭\₡\₦\₾\₩\₪\₫\₱\₲\₴\₸\₺\₼\₽\₹]', '', budget).replace(' ', '').replace('?', '').replace('(estimated)', '').replace(',', '')
        return cleaned_budget

    def clean_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return date_str

    def convert_to_float(self, str_val):
        return float(str_val.replace(' ', '').replace('k', '000').replace('M', '000000'))

    def convert_timing_to_minutes(self, timing_str):
        match = re.search(r'(?:(\d+)h)?\s*(?:(\d+)min)?', timing_str)
        if not match:
            return timing_str
        hours, minutes = match.groups(default='0')
        return int(hours) * 60 + int(minutes)

    def clean_director_names(self, directors_list):
        return ','.join(name for name in directors_list if name not in ['De', 'Par'])

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
    
    
