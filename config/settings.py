from pathlib import Path
import os
import secrets
from dotenv import load_dotenv

load_dotenv()
# --- EMAIL CONFIGURATION ---
# Configuración para enviar correos usando Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'vmorinigo31@gmail.com'
EMAIL_HOST_PASSWORD = 'nxoludpbghkaimak'
# ⚠️ Ignora verificación SSL
import ssl
import certifi
EMAIL_SSL_CONTEXT = ssl._create_unverified_context()  # ⚠️ solo desarrollo

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-' + secrets.token_urlsafe(50))
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# --- URLS ---
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',  # tu app
    'core',
    'administrativo',
    'contable',
    'juridico',
    'caja',
    'reportes',
    'widget_tweaks',
    "django_crontab",
    'django_apscheduler',

]
CRONJOBS = [
    # todos los días a las 07:00
    ("0 7 * * *", "contable.utils.enviar_alertas_vencimientos"),
]
# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',       # obligatorio
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # obligatorio
    'django.contrib.messages.middleware.MessageMiddleware',       # obligatorio
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'recepcion_docs',
        'USER': 'postgres',
        'PASSWORD': '123456789',  # Cambia por tu contraseña real
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# --- PASSWORD VALIDATORS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# --- MEDIA FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- DEFAULTS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- LOGIN/LOGOUT ---
# A dónde redirige si no está logueado
LOGIN_URL = 'login'

# A dónde redirige después de iniciar sesión
LOGIN_REDIRECT_URL = 'index'  

# A dónde va después de cerrar sesión (opcional)
LOGOUT_REDIRECT_URL = 'login'

# --- EMAIL (para desarrollo, usa consola) ---
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = 'vmorinigo31@gmail.com'
#EMAIL_HOST_PASSWORD = 'nxoludpbghkaimak'  # tu App Password sin espacios
#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Tiempo de sesión en segundos (ej: 30 días)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 días

# Para que la sesión no se borre al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# Lista de destinatarios internos (los que deben recibir las alertas)
VENCIMIENTOS_RECIPIENTES = [
    "victor.morinigo06@unae.edu.py",
]
