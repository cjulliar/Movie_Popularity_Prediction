from datetime import datetime
import logging
import pytz

from django.conf import settings
from django.core.management.base import BaseCommand

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from dashboard.utils import get_initial_movies, get_next_movies, get_old_movies, update_custom_dates


logger = logging.getLogger(__name__)


@util.close_old_connections
def init_db_job():
    update_custom_dates()
    get_initial_movies()
    get_next_movies()


@util.close_old_connections
def next_movies_job():
    update_custom_dates()
    get_next_movies()


@util.close_old_connections
def old_movies_job():
    get_old_movies()


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  """
  This job deletes APScheduler job execution entries older than `max_age` from the database.
  It helps to prevent the database from filling up with old historical records that are no
  longer useful.
  
  :param max_age: The maximum length of time to retain historical job execution records.
                  Defaults to 7 days.
  """
  DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
  help = "Runs APScheduler."

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Tâche pour initialiser la base de données
    scheduler.add_job(
       init_db_job, 
       'date', 
       run_date=datetime(2024, 4, 24, 10, 0, 0), 
       timezone=pytz.timezone('CET'),
       id="initiate_job",
       max_instances=1,
       replace_existing=True,
    )
    logger.info("Added one time job 'initiate_job'.")

    # Tâche pour récupérer les prochains films chaque lundi matin
    scheduler.add_job(
      next_movies_job, 
      trigger='cron', 
      day_of_week='mon',
      hour=8,
      minute=55,
      timezone=pytz.timezone('CET'),
      id="next_movie_job",
      max_instances=1,
      replace_existing=True,
    )
    logger.info("Added weekly job: 'next_movie_job'.")    
    
    # Tâche pour récupérer les entrées des films chaque jeudi après-midi
    scheduler.add_job(
      old_movies_job, 
      trigger='cron', 
      day_of_week='thu',
      hour=13,
      minute=55,
      timezone=pytz.timezone('CET'),
      id="old_movie_job",
      max_instances=1,
      replace_existing=True,
    )
    logger.info("Added weekly job: 'old_movie_job'.")

    # Tâche pour supprimer les logs des précédentes tâches
    scheduler.add_job(
      delete_old_job_executions,
      trigger=CronTrigger(
        day_of_week="mon", hour="00", minute="00"
      ),  # Midnight on Monday, before start of the next work week.
      id="delete_old_job_executions",
      max_instances=1,
      replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    try:
      logger.info("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      logger.info("Stopping scheduler...")
      scheduler.shutdown()
      logger.info("Scheduler shut down successfully!")