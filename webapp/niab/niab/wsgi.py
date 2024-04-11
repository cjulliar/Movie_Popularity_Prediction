"""
WSGI config for niab project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import pathlib

import dotenv

from django.core.wsgi import get_wsgi_application

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
ENV_FILE_PATH = BASE_DIR / '.env'

dotenv.read_dotenv(str(ENV_FILE_PATH), override=True)

environment = os.getenv("ENVIRONMENT")

if environment == "dev":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niab.settings.dev')
elif environment == "prod":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niab.settings.prod')

application = get_wsgi_application()
