from dashboard.utils import get_initial_movies, get_next_movies, get_old_movies, update_custom_dates
from dashboard.utils import get_initial_movies, tmp_get_old_movies


def init_db_job():
    get_initial_movies()


def next_movies_job():
    update_custom_dates()
    get_next_movies()


def old_movies_job():
    get_old_movies()


def tmp_db_job():
    update_custom_dates()
    tmp_get_old_movies()
    get_next_movies()