from pathlib import Path
import os

import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعداد Cloudinary
cloudinary.config( 
    cloud_name = os.getenv('CLOUD_NAME'), 
    api_key = os.getenv('API_KEY'), 
    api_secret = os.getenv('API_SECRET'),
    secure=True
)

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# إعدادات الأمان
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key')
DEBUG = True
ALLOWED_HOSTS = ['mansoour.onrender.com', '127.0.0.1', 'localhost']

# التطبيقات المثبتة
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # تطبيقات المشروع
    'core',
    'widget_tweaks',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
]

# الميدل وير
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

# إعدادات URLs
ROOT_URLCONF = 'real_estate_platform.urls'

# إعدادات القوالب
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# إعدادات WSGI
WSGI_APPLICATION = 'real_estate_platform.wsgi.application'

# قاعدة البيانات (SQLite)
import dj_database_url

DATABASES = {
'default': dj_database_url.config(default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
}


# تحقق كلمة المرور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# اللغة والتوقيت
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# نموذج المستخدم
AUTH_USER_MODEL = 'core.CustomUser'

# ملفات static
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات Cloudinary لتخزين media
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# روابط تسجيل الدخول والخروج
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

# نوع المفتاح الأساسي الافتراضي
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


print("CLOUD_NAME =", os.getenv('CLOUD_NAME'))
print("API_KEY =", os.getenv('API_KEY'))
print("API_SECRET =", os.getenv('API_SECRET'))
