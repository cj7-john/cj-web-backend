"""
CJ Web Studio — Django Settings
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-insecure-key-change-this-before-you-deploy-cjwebstudio-2025!'
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Fix for browsers sending requests with port
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    "https://cj-web-design-studio.netlify.app",
]

# ── INSTALLED APPS ────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'quotes',
    'corsheaders',
]

# ── MIDDLEWARE ────────────────────────────────────────────────────────────
MIDDLEWARE = [
     "corsheaders.middleware.CorsMiddleware",  # must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'cj_studio.urls'

# ── TEMPLATES ─────────────────────────────────────────────────────────────
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
                # Makes AGENCY dict available in all templates automatically
                'quotes.context_processors.agency_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'cj_studio.wsgi.application'

# ── DATABASE ──────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── AUTH ──────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── LOCALISATION ──────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Johannesburg'
USE_I18N      = True
USE_TZ        = True

# ── STATIC FILES ──────────────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── EMAIL ─────────────────────────────────────────────────────────────────
#
# DEVELOPMENT — emails print to your terminal (default):
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# PRODUCTION — switch to this once you have your Gmail App Password:
# -----------------------------------------------------------------------
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'cibangukaj@gmail.com'
EMAIL_HOST_PASSWORD = 'onkz utrk gfni vtbc'   # <-- must be in quotes
DEFAULT_FROM_EMAIL  = 'CJ Web Studio <cibangukaj@gmail.com>'
# -----------------------------------------------------------------------

#
# HOW TO GET THE APP PASSWORD:
# 1. myaccount.google.com → Security → 2-Step Verification (turn on)
# 2. myaccount.google.com → Security → App Passwords
# 3. Create → Mail → Other → name it "Django CJ Studio"
# 4. Copy the 16-char password → paste above as EMAIL_HOST_PASSWORD

DEFAULT_FROM_EMAIL = 'CJ Web Studio <cibangukaj@gmail.com>'

# ── AGENCY CONFIG ─────────────────────────────────────────────────────────
# Used in emails, invoices, and templates via context processor
ADMIN_EMAIL = 'cibangukaj@gmail.com'

AGENCY = {
    'name':    'CJ Web Studio',
    'owner':   'John Buhendwa',
    'email':   'cibangukaj@gmail.com',
    'phone':   '+27 81 795 7533',
    'location':'Durban, South Africa',
    'website': 'http://127.0.0.1:8000',   # Update to your domain when live
    'vat_no':  '',
    'bank': {
        'name':        'First National Bank',
        'account':     '',        # Add your account number
        'branch_code': '',        # Add your branch code
    },
    'deposit_percent': 50,
}

# ── LOGGING ───────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'quotes': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# ── CORS ────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://cj-web-design-studio.netlify.app",
]

# Allow your Netlify domain
CORS_ALLOWED_ORIGINS = [
    "https://cj-web-design-studio.netlify.app",
]

# Optional: allow all methods/headers
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
