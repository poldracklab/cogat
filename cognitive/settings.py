"""
Django settings for cognitive atlas project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import sys
import os
from os.path import join, abspath, dirname

from py2neo import Graph
from py2neo.neo4j import authenticate

# Just for local development - will read this from secrets
graph = Graph("http://graphdb:7474/db/data/")
#authenticate("127.0.0.1:7474", "neo4j", "neo4j")
#graph = Graph()

DOMAIN = "http://www.cognitiveatlas.org"

# PATH vars
here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here(".")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)
sys.path.insert(0, root('apps'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

ALLOWED_HOSTS = ["*"]
SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'cognitive.apps.main',
    'cognitive.apps.atlas',
    'cognitive.apps.users',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
]
#    'allauth',
#    'allauth.account',
#    'allauth.socialaccount',
#    'allauth.socialaccount.providers.dropbox',
#    'allauth.socialaccount.providers.dropbox_oauth2',
#    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.github',
#    'allauth.socialaccount.providers.gitlab',
#    'allauth.socialaccount.providers.google',
#    'allauth.socialaccount.providers.linkedin',
#    'allauth.socialaccount.providers.linkedin_oauth2',
#    'allauth.socialaccount.providers.openid',
#    'allauth.socialaccount.providers.orcid',
#    'allauth.socialaccount.providers.stackexchange',
#    'allauth.socialaccount.providers.twitter',

INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cognitive.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# CUSTOM CONTEXT PROCESSORS
TEMPLATES[0]['OPTIONS']['context_processors'].append("main.context_processors.counts_processor")

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

WSGI_APPLICATION = 'cognitive.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_NAME', ''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher',
]



# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

MEDIA_ROOT = '/var/www/assets'
MEDIA_URL = '/assets/'
STATIC_ROOT = '/var/www/static'
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
}

AUTH_USER_MODEL = 'users.User'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'verybadnotgoodsecretkeythatisntsecret')
DEBUG = os.environ.get('DJANGO_DEBUG', False)
