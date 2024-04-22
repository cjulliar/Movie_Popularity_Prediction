from datetime import datetime
import pytz
import threading

from .jobs import init_db_job, next_movies_job, old_movies_job
from .jobs import tmp_db_job

from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler()
lock = threading.Lock()

def start_scheduler():
    global scheduler
    global lock
    with lock:
        if not scheduler.running:
            scheduler.add_job(init_db_job, 'date', run_date=datetime(2024, 4, 23, 12, 0, 0), timezone=pytz.timezone('CET'))
            scheduler.add_job(tmp_db_job, 'date', run_date=datetime(2024, 4, 20, 20, 23, 0), timezone=pytz.timezone('CET'))
            scheduler.add_job(next_movies_job, trigger='cron', day_of_week='mon', hour=8, minute=55, timezone=pytz.timezone('CET'))
            scheduler.add_job(old_movies_job, trigger='cron', day_of_week='thu', hour=12, minute=00, timezone=pytz.timezone('CET'))
            scheduler.start()