from datetime import datetime
import pytz
import threading

from .jobs import init_db_job, next_movies_job, old_movies_job, tmp_test

from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler()
lock = threading.Lock()

def start_scheduler():
    global scheduler
    global lock
    with lock:
        if not scheduler.running:
            scheduler.add_job(init_db_job, 'date', run_date=datetime(2024, 4, 25, 9, 30, 0), timezone=pytz.timezone('CET'))
            scheduler.add_job(next_movies_job, trigger='cron', day_of_week='mon', hour=8, minute=55, timezone=pytz.timezone('CET'))
            scheduler.add_job(old_movies_job, trigger='cron', day_of_week='thu', hour=14, minute=00, timezone=pytz.timezone('CET'))
            scheduler.add_job(tmp_test, 'date', run_date=datetime(2024, 4, 23, 11, 35, 0), timezone=pytz.timezone('CET'))
            scheduler.start()