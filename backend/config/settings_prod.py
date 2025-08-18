from .settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# Hosts permitidos
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    '.vercel.app',
    os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', ''),
    os.environ.get('VERCEL_URL', ''),
]

# Remove hosts vazios
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Database para produção
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback para SQLite em desenvolvimento
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuração do WhiteNoise para servir arquivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files - usar cloud storage em produção
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS settings para produção
CORS_ALLOWED_ORIGINS = [
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

# Adicionar domínios de produção via variável de ambiente
if os.environ.get('CORS_ALLOWED_ORIGINS'):
    CORS_ALLOWED_ORIGINS.extend(
        os.environ.get('CORS_ALLOWED_ORIGINS').split(',')
    )

# Permitir credenciais
CORS_ALLOW_CREDENTIALS = True

# Configurações de segurança para produção
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # SSL settings (descomente quando tiver SSL)
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True

# Configurações de cache com Redis (se disponível)
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

# Configurações de email para produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Configurações de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# WhatsApp API settings
WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', '')
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')

# Configurações específicas do Railway
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Usar PORT fornecido pelo Railway
    PORT = os.environ.get('PORT', '8000')
    
    # Configurar ALLOWED_HOSTS para Railway
    if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        ALLOWED_HOSTS.append(os.environ.get('RAILWAY_PUBLIC_DOMAIN'))
    
    # Configurar CORS para Railway
    if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        CORS_ALLOWED_ORIGINS.append(f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}")

# REST Framework settings para produção
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
})

print(f"🚀 Produção configurada!")
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"DATABASE: {'PostgreSQL' if 'DATABASE_URL' in os.environ else 'SQLite'}")
print(f"CORS_ORIGINS: {len(CORS_ALLOWED_ORIGINS)} origens")