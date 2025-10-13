import os
from pathlib import Path
from dotenv import load_dotenv

import dj_database_url
# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY must be set in environment variables')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else ['localhost', '127.0.0.1', 'healthkart360-backend.onrender.com']
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError('ALLOWED_HOSTS must be set in production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'users',
    'pharmacy',
    'medicines',
    'orders',
    'reminders',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.RateLimitMiddleware',
    'core.middleware.SecurityLoggingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

ROOT_URLCONF = 'healthkart360.urls'

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
                'core.context_processors.language_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'healthkart360.wsgi.application'

# Database
# Database configuration using dj-database-url
# For local development, your .env file can look like:
# DATABASE_URL=postgres://user:password@localhost:5432/healthkart360
# For production, you'll get this URL from your provider (e.g., Supabase, Neon).
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
else:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Password validation
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
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Languages
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिंदी (Hindi)'),
    ('mr', 'मराठी (Marathi)'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# For Gmail, use smtp.gmail.com. For other providers, use their SMTP server.
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# Enter your real email address and an App Password (not your normal password)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# Pharmacist email for receiving prescription verification codes
PHARMACIST_EMAIL = 'omninawe27@gmail.com'  # Change this to the actual pharmacist email

# Site URL for email links
SITE_URL = 'http://localhost:8000'  # Change this to your production URL

# Razorpay Test Mode Keys
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# File upload security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_NUMBER_FILES = 10

# Rate limiting (simple implementation)
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 1000))  # Temporarily increased for load testing
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 3600))  # 1 hour

# IMPORTANT:
# - For Gmail, you must enable 2-Step Verification and create an App Password.
# - Do NOT use your normal Gmail password here.
# - For other providers, use their recommended SMTP settings and credentials.
