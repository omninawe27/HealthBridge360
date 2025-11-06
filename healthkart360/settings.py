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

ALLOWED_HOSTS = []

# Add Render.com's external hostname to the allowed hosts
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add the service host from Render
SERVICE_HOST = os.environ.get('RENDER_SERVICE_HOST')
if SERVICE_HOST:
    ALLOWED_HOSTS.append(SERVICE_HOST)

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
else:
    # In production, allow the backend service host
    ALLOWED_HOSTS.extend(['healthbridge360-backend.onrender.com', 'healthkart360-backend.onrender.com'])
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
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
if DATABASE_URL and DATABASE_URL != 'postgresql://user:password@host:port/database':
    try:
        DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
    except Exception as e:
        # Fallback to SQLite for development if DATABASE_URL is malformed or any error occurs
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        print("WARNING: DATABASE_URL is malformed or invalid, falling back to SQLite for development.")
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    if DATABASE_URL == 'postgresql://user:password@host:port/database':
        print("INFO: DATABASE_URL contains placeholder values, using SQLite for development.")
    else:
        print("INFO: DATABASE_URL not set, using SQLite for development.")

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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


# Email configuration - Use SendGrid backend in production
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
if DEBUG and not SENDGRID_API_KEY:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@healthbridge360.sendgrid.net')

# Debug logging for email configuration
# print(f"DEBUG: SENDGRID_API_KEY is set: {bool(SENDGRID_API_KEY)}")
# print(f"DEBUG: SENDGRID_API_KEY starts with SG: {SENDGRID_API_KEY and SENDGRID_API_KEY.startswith('SG.')}")


# For local development or when SendGrid API key is not set, use console backend
# if not SENDGRID_API_KEY or not SENDGRID_API_KEY.startswith('SG.') or SENDGRID_API_KEY in ['your-sendgrid-api-key', 'placeholder_sendgrid_api_key']:
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#     print("WARNING: No valid SendGrid API key found. Using console email backend.")
#     print(f"DEBUG: SENDGRID_API_KEY value: '{SENDGRID_API_KEY}'")
# else:
#     print("Email configured with SendGrid backend.")


# Pharmacist email for receiving prescription verification codes
PHARMACIST_EMAIL = os.getenv('PHARMACIST_EMAIL', 'omninawe27@gmail.com')

# Site URL for email links
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

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

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Use Redis if available in production
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

# Celery Configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# IMPORTANT:
# - For Gmail, you must enable 2-Step Verification and create an App Password.
# - Do NOT use your normal Gmail password here.
# - For other providers, use their recommended SMTP settings and credentials.
