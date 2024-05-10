from dashboard.utils import get_initial_movies, get_next_movies, get_old_movies, update_custom_dates


def init_db_job():
    update_custom_dates()
    get_initial_movies()
    get_next_movies()


def next_movies_job():
    update_custom_dates()
    get_next_movies()


def old_movies_job():
    get_old_movies()