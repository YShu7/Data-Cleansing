"""
Django settings for datacleansing project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+=i)q#_ah^m!pocnlb!_z=2e9!zn^nfc4h-_8!i81i*6fzcs*q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'pages.apps.PagesConfig',
    'authentication.apps.AuthenticationConfig',
    'assign.apps.AssignConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'datacleansing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'datacleansing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travisci',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'datacleansing',
            'USER': 'datacleansinguser', # input your user name
            'PASSWORD': 'L1feI5T0ugh', # input your password
            'HOST': 'localhost',
            'PORT': '',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Customize authentication
AUTH_USER_MODEL = 'authentication.CustomUser'
AUTHENTICATION_BACKENDS = ('authentication.backends.CustomBackend',)

# Set the redirect links for login and logout to home template
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "a874257217@gmail.com"
EMAIL_HOST_PASSWORD = "bdxaqbvjmmpswitr"
EMAIL_USE_TLS = True
EMAIL_FROM = "Data Cleansing Team <noreply@gmail.com>"


ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'
MSG_FAIL_CHOICE = "Please choose an answer."
MSG_FAIL_DATA_NONEXIST = "Data #{} doesn't exist."
MSG_FAIL_LABEL_NONEXIST = "Label #{} doesn't exist."

MSG_SUCCESS_REG = "User registration succeed"
MSG_FAIL_EMAIL = "Email {} has been used"
MSG_FAIL_CERTI = "Certificate {} has been used"
MSG_FAIL_FILL = "Please fill in {}."
MSG_FAIL_DEL_GRP = "Group names didn't match."

MSG_SUCCESS_VOTE = "Update Succeed."
MSG_SUCCESS_VAL = "Update Succeed."
MSG_SUCCESS_PWD_CHANGE = "Password was changed."
MSG_SUCCESS_SIGN_UP = "Sign up successfully."
MSG_SUCCESS_RETRY = "Your request has been sent."
MSG_SUCCESS_ASSIGN = "Assign Tasks Succeed"
MSG_SUCCESS_SUM = "Summarize Succeed"
MSG_SUCCESS_IMPORT = "Database is successfully imported. Click 'Assign Tasks' to re-assign all tasks to users."
MSG_SUCCESS_DEL_GRP = "Group {} was successfully deleted."
MSG_SUCCESS_CRT_GRP = "Group {} was successfully created."

VAL = "validate"
VOT = "vote"
SEL = "select"

CORRECT_POINT = 3
INCORRECT_POINT = 1