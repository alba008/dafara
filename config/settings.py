import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv('DEBUG', '0') == '1'
DEMO_MODE = os.getenv('DEMO_MODE', '1') == '1'
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG: raise RuntimeError('Set SECRET_KEY before starting')
    SECRET_KEY = 'local-development-only-not-for-production'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
CSRF_TRUSTED_ORIGINS = [x for x in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if x]
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','core.context.brand']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
if os.getenv('POSTGRES_HOST'):
    DATABASES = {'default':{'ENGINE':'django.db.backends.postgresql','HOST':os.environ['POSTGRES_HOST'],'NAME':os.environ['POSTGRES_DB'],'USER':os.environ['POSTGRES_USER'],'PASSWORD':os.environ['POSTGRES_PASSWORD'],'PORT':'5432'}}
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='America/New_York'
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/login/'
LOGIN_REDIRECT_URL='/management/'
LOGOUT_REDIRECT_URL='/'
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT','0') == '1'
SESSION_COOKIE_SECURE = os.getenv('COOKIE_SECURE', '0' if DEBUG else '1') == '1'
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
