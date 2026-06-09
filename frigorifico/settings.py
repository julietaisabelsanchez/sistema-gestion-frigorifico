from pathlib import Path
from datetime import timedelta
import os
import dj_database_url

# 📁 BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 SEGURIDAD
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-temporal')

DEBUG = True

ALLOWED_HOSTS = [
    "web-production-3ad00.up.railway.app",
    "web-production-76047.up.railway.app",
    "web-frigorificochicoana.up.railway.app",
    "web-frigorificochicoana.com-ar",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://web-production-3ad00.up.railway.app",
    "https://web-production-76047.up.railway.app",
    "https://web-frigorificochicoana.up.railway.app",
    "https://web-frigorificochicoana.com-ar",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# 🧩 APLICACIONES
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',
    
    'rest_framework',
    'gestion',
]

# ⚙️ MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🔗 URLS
ROOT_URLCONF = 'frigorifico.urls'


# 🖥️ TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'gestion/templates'],
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

# 🚀 WSGI
WSGI_APPLICATION = 'frigorifico.wsgi.application'

# 🗄️ BASE DE DATOS
_pg_host = os.environ.get('PGHOST', 'localhost')
_pg_port = os.environ.get('PGPORT', '5432')
_pg_user = os.environ.get('PGUSER', 'postgres')
_pg_password = os.environ.get('PGPASSWORD', '')
_pg_database = os.environ.get('PGDATABASE', 'railway')
_local_db_url = f"postgresql://{_pg_user}:{_pg_password}@{_pg_host}:{_pg_port}/{_pg_database}"

DATABASES = {
    'default': dj_database_url.config(
        default=_local_db_url,
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# 🔐 PASSWORDS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 IDIOMA
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True
USE_TZ = True

# 📦 ARCHIVOS ESTÁTICOS
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static'),
#]
# WhiteNoise (producción)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 🔐 LOGIN
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# 🔑 DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# 🔐 JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 📊 CONFIG EXTRA
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Email backend: usar consola en desarrollo para pruebas de restablecimiento
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'