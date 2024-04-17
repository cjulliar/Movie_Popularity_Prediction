"""
ASGI config for niab project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import pathlib

import dotenv

from django.core.asgi import get_asgi_application

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
ENV_FILE_PATH = BASE_DIR / '.env'

dotenv.read_dotenv(str(ENV_FILE_PATH), override=True)

environment = os.getenv("ENVIRONMENT")

if environment == "dev":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niab.settings.dev')
elif environment == "prod":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niab.settings.prod')

application = get_asgi_application()
