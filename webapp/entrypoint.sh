#!/bin/sh

python3 manage.py makemigrations && python3 manage.py migrate 


python3 manage.py collectstatic --no-input

# Prod
gunicorn niab.wsgi:application --workers=4 --timeout 120 --bind=0.0.0.0:8000

#Dev
# python3 manage.py runserver 0.0.0.0:8000