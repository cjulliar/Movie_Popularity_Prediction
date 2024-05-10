FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron


WORKDIR /ml


COPY models/model_cb.pkl /ml/
# COPY model_prochaines_sorties.ipynb /ml/
COPY test_cron.py /ml/
# COPY prediction_dans_bdd_sql.ipynb /ml/

# RUN pip install -r requirements.txt
# RUN python3 test_cron.py >> resultat.log

RUN echo ------- >> resultat2.log
RUN echo "Heure du serveur : $(date)" >> resultat2.log

COPY cronjob /ml/

RUN chmod 777 /ml/cronjob
RUN chmod 777 /ml/test_cron.py

RUN crontab cronjob


CMD ["cron", "-f"]



