import os
from pathlib import Path

# Répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète (à remplacer en production)
SECRET_KEY = 'django-insecure-aviatorbot-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['aviatorweb.onrender.com']  # À restreindre en production

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'aviator',  # Notre app principale
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aviatorbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'aviator' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aviatorbot.wsgi.application'

# Base de données SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Mot de passe
AUTH_PASSWORD_VALIDATORS = []

# Langue et fuseau
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Maputo'

USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'aviator' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
