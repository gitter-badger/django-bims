# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
import os
import re
import ast
import sys
from datetime import timedelta
from distutils.util import strtobool  # noqa
from urllib.parse import urlparse, urlunparse, urljoin

import django
import dj_database_url
#
# General Django development settings
#
from django.conf.global_settings import DATETIME_INPUT_FORMATS
from kombu import Queue, Exchange

SILENCED_SYSTEM_CHECKS = [
    '1_8.W001',
    'fields.W340',
    'auth.W004',
    'urls.W002'
]

DEFAULT_CHARSET = "utf-8"

# Defines the directory that contains the settings file as the PROJECT_ROOT
# It is used for relative settings elsewhere.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Setting debug to true makes Django serve static media and
# present pretty error pages.
DEBUG = ast.literal_eval(os.getenv('DEBUG', 'True'))

# Set to True to load non-minified versions of (static) client dependencies
# Requires to set-up Node and tools that are required for static development
# otherwise it will raise errors for the missing non-minified dependencies
DEBUG_STATIC = ast.literal_eval(os.getenv('DEBUG_STATIC', 'False'))

FORCE_SCRIPT_NAME = os.getenv('FORCE_SCRIPT_NAME', '')

# Define email service on GeoNode
EMAIL_ENABLE = ast.literal_eval(os.getenv('EMAIL_ENABLE', 'False'))

if EMAIL_ENABLE:
    EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND',
                              default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', 'localhost')
    EMAIL_PORT = os.getenv('DJANGO_EMAIL_PORT', 25)
    EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = ast.literal_eval(os.getenv('DJANGO_EMAIL_USE_TLS', 'False'))
    EMAIL_USE_SSL = ast.literal_eval(os.getenv('DJANGO_EMAIL_USE_SSL', 'False'))
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'GeoNode <no-reply@geonode.org>')
else:
    EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND',
                              default='django.core.mail.backends.console.EmailBackend')

# Make this unique, and don't share it with anybody.
_DEFAULT_SECRET_KEY = 'myv-y4#7j-d*p-__@j#*3z@!y24fz8%^z2v6atuy4bo9vqr1_a'
SECRET_KEY = os.getenv('SECRET_KEY', _DEFAULT_SECRET_KEY)

SITE_HOST_SCHEMA = os.getenv('SITE_HOST_SCHEMA', 'http')
SITE_HOST_NAME = os.getenv('SITE_HOST_NAME', 'localhost')
SITE_HOST_PORT = os.getenv('SITE_HOST_PORT', 8000)
_default_siteurl = "%s://%s:%s/" % (SITE_HOST_SCHEMA,
                                    SITE_HOST_NAME,
                                    SITE_HOST_PORT) if SITE_HOST_PORT else "%s://%s/" % (SITE_HOST_SCHEMA, SITE_HOST_NAME)
SITEURL = os.getenv('SITEURL', _default_siteurl)

# we need hostname for deployed
_surl = urlparse(SITEURL)
HOSTNAME = _surl.hostname

# add trailing slash to site url. geoserver url will be relative to this
if not SITEURL.endswith('/'):
    SITEURL = '{}/'.format(SITEURL)

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///{path}'.format(
        path=os.path.join(PROJECT_ROOT, 'development.db')
    )
)

# DATABASE_URL = 'postgresql://test_geonode:test_geonode@localhost:5432/geonode'

# Defines settings for development

# since GeoDjango is in use, you should use gis-enabled engine, for example:
# 'ENGINE': 'django.contrib.gis.db.backends.postgis'
# see https://docs.djangoproject.com/en/1.8/ref/contrib/gis/db-api/#module-django.contrib.gis.db.backends for
# detailed list of supported backends and notes.
GEONODE_DB_CONN_MAX_AGE = int(os.getenv('GEONODE_DB_CONN_MAX_AGE', 0))
GEONODE_DB_CONN_TOUT = int(os.getenv('GEONODE_DB_CONN_TOUT', 5))

_db_conf = dj_database_url.parse(
    DATABASE_URL,
    conn_max_age=GEONODE_DB_CONN_MAX_AGE)
if 'spatialite' in DATABASE_URL:
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite.so'

if 'CONN_TOUT' in _db_conf:
    _db_conf['CONN_TOUT'] = GEONODE_DB_CONN_TOUT
if 'postgresql' in DATABASE_URL or 'postgis' in DATABASE_URL:
    if 'OPTIONS' not in _db_conf:
        _db_conf['OPTIONS'] = {}
    _db_conf['OPTIONS'].update({
        'connect_timeout': GEONODE_DB_CONN_TOUT,
    })

DATABASES = {
    'default': _db_conf
}

if os.getenv('DEFAULT_BACKEND_DATASTORE'):
    GEODATABASE_URL = os.getenv('GEODATABASE_URL',
                                'postgis://\
geonode_data:geonode_data@localhost:5432/geonode_data')
    DATABASES[os.getenv('DEFAULT_BACKEND_DATASTORE')] = dj_database_url.parse(
        GEODATABASE_URL, conn_max_age=GEONODE_DB_CONN_MAX_AGE
    )
    _geo_db = DATABASES[os.getenv('DEFAULT_BACKEND_DATASTORE')]
    if 'CONN_TOUT' in DATABASES['default']:
        _geo_db['CONN_TOUT'] = DATABASES['default']['CONN_TOUT']
    if 'postgresql' in GEODATABASE_URL or 'postgis' in GEODATABASE_URL:
        _geo_db['OPTIONS'] = DATABASES['default']['OPTIONS'] if 'OPTIONS' in DATABASES['default'] else {}
        _geo_db['OPTIONS'].update({
            'connect_timeout': GEONODE_DB_CONN_TOUT,
        })

    DATABASES[os.getenv('DEFAULT_BACKEND_DATASTORE')] = _geo_db

# If set to 'True' it will refresh/regenrate all resource links everytime a 'migrate' will be performed
UPDATE_RESOURCE_LINKS_AT_MIGRATE = ast.literal_eval(os.getenv('UPDATE_RESOURCE_LINKS_AT_MIGRATE', 'False'))

MANAGERS = ADMINS = os.getenv('ADMINS', [])

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = os.getenv('TIME_ZONE', "UTC")

SITE_ID = int(os.getenv('SITE_ID', '1'))

USE_TZ = True
USE_I18N = ast.literal_eval(os.getenv('USE_I18N', 'True'))
USE_L10N = ast.literal_eval(os.getenv('USE_I18N', 'True'))

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', "en")

_DEFAULT_LANGUAGES = """(
    ('af', 'Afrikaans'),
    ('sq', 'Albanian'),
    ('am', 'Amharic'),
    ('ar', 'Arabic'),
    ('id', 'Bahasa Indonesia'),
    ('bn', 'Bengali'),
    ('de', 'Deutsch'),
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('it', 'Italiano'),
    ('km', 'Khmer'),
    ('nl', 'Nederlands'),
    ('ne', 'Nepali'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('pt-br', 'Portuguese (Brazil)'),
    ('ru', 'Russian'),
    ('si', 'Sinhala'),
    ('sw', 'Swahili'),
    ('sv', 'Swedish'),
    ('tl', 'Tagalog'),
    ('ta', 'Tamil'),
    ('uk', 'Ukranian'),
    ('vi', 'Vietnamese'),
    ('el', 'Ελληνικά'),
    ('th', 'ไทย'),
    ('zh-cn', '中文'),
    ('ja', '日本語'),
    ('ko', '한국어'),
)"""

LANGUAGES = ast.literal_eval(os.getenv('LANGUAGES', _DEFAULT_LANGUAGES))

EXTRA_LANG_INFO = {
    'am': {
        'bidi': False,
        'code': 'am',
        'name': 'Amharic',
        'name_local': 'Amharic',
    },
    'tl': {
        'bidi': False,
        'code': 'tl',
        'name': 'Tagalog',
        'name_local': 'tagalog',
    },
    'ta': {
        'bidi': False,
        'code': 'ta',
        'name': 'Tamil',
        'name_local': 'tamil',
    },
    'si': {
        'bidi': False,
        'code': 'si',
        'name': 'Sinhala',
        'name_local': 'sinhala',
    },
}

AUTH_USER_MODEL = os.getenv('AUTH_USER_MODEL', 'people.Profile')

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
    # 'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    # 'django.contrib.auth.hashers.BCryptPasswordHasher',
]

MODELTRANSLATION_LANGUAGES = ['en', ]
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en',)

# Location of url mappings

# ########################################################################### #
# MEDIA / STATICS STORAGES SETTINGS
# ########################################################################### #

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'uploaded'
THUMBNAIL_LOCATION = 'thumbs'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(PROJECT_ROOT, MEDIAFILES_LOCATION))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = os.getenv('MEDIA_URL', '%s/%s/' % (FORCE_SCRIPT_NAME, MEDIAFILES_LOCATION))
LOCAL_MEDIA_URL = os.getenv('LOCAL_MEDIA_URL', '%s/%s/' % (FORCE_SCRIPT_NAME, MEDIAFILES_LOCATION))

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.getenv('STATIC_ROOT',
                        os.path.join(PROJECT_ROOT, 'static_root')
                        )

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = os.getenv('STATIC_URL', '%s/%s/' % (FORCE_SCRIPT_NAME, STATICFILES_LOCATION))

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# AWS S3 Settings
S3_STATIC_ENABLED = ast.literal_eval(os.environ.get('S3_STATIC_ENABLED', 'False'))
S3_MEDIA_ENABLED = ast.literal_eval(os.environ.get('S3_MEDIA_ENABLED', 'False'))

# Required to run Sync Media to S3
AWS_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '')

AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_S3_BUCKET_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Cache Bustin Settings
CACHE_BUSTING_STATIC_ENABLED = ast.literal_eval(os.environ.get('CACHE_BUSTING_STATIC_ENABLED', 'False'))
CACHE_BUSTING_MEDIA_ENABLED = ast.literal_eval(os.environ.get('CACHE_BUSTING_MEDIA_ENABLED', 'False'))

if not DEBUG and not S3_STATIC_ENABLED and not S3_MEDIA_ENABLED:
    if CACHE_BUSTING_STATIC_ENABLED or CACHE_BUSTING_MEDIA_ENABLED:
        from django.contrib.staticfiles import storage
        storage.ManifestStaticFilesStorage.manifest_strict = False
    if CACHE_BUSTING_STATIC_ENABLED:
        STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
    if CACHE_BUSTING_MEDIA_ENABLED:
        DEFAULT_FILE_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

CACHES = {
    # DUMMY CACHE FOR DEVELOPMENT
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'resources': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 600,
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    }
}

MEMCACHED_ENABLED = ast.literal_eval(os.getenv('MEMCACHED_ENABLED', 'False'))
MEMCACHED_BACKEND = os.getenv('MEMCACHED_BACKEND', 'django.core.cache.backends.memcached.MemcachedCache')
MEMCACHED_LOCATION = os.getenv('MEMCACHED_LOCATION', '127.0.0.1:11211')
MEMCACHED_LOCK_EXPIRE = int(os.getenv('MEMCACHED_LOCK_EXPIRE', 3600))
MEMCACHED_LOCK_TIMEOUT = int(os.getenv('MEMCACHED_LOCK_TIMEOUT', 10))

if MEMCACHED_ENABLED:
    CACHES['default'] = {
        'BACKEND': MEMCACHED_BACKEND,
        'LOCATION': MEMCACHED_LOCATION,
    }

GEONODE_CORE_APPS = (
    # GeoNode internal apps
    # 'geonode.api',
    'geonode.base',
    # 'geonode.br',
    # 'geonode.layers',
    # 'geonode.maps',
    'geonode.documents',
    # 'geonode.security',
    # 'geonode.catalogue',
    # d'geonode.catalogue.metadataxsl',
)

GEONODE_INTERNAL_APPS = (
    # GeoNode internal apps
    'geonode.people',
    # 'geonode.client',
    # 'geonode.themes',
    # 'geonode.proxy',
    # 'geonode.social',
    'geonode.groups',
    # 'geonode.services',
)

# Uncomment the following line to enable contrib apps
GEONODE_APPS = GEONODE_CORE_APPS + GEONODE_INTERNAL_APPS

INSTALLED_APPS = (

    # Boostrap admin theme
    # 'django_admin_bootstrapped.bootstrap3',
    # 'django_admin_bootstrapped',

    # Apps bundled with Django
    'modeltranslation',
    'dal',
    'dal_select2',
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.gis',

    # Utility
    'dj_pagination',
    'taggit',
    'treebeard',
    # 'leaflet',
    # 'bootstrap3_datetime',
    'django_filters',
    'mptt',

    # Theme
    # 'django_forms_bootstrap',

    # Social
    # 'avatar',
    # 'dialogos',
    # 'pinax.ratings',
    'polymorphic',
    'guardian',
    'oauth2_provider',
    'corsheaders',
    'invitations',

    # login with external providers
    'allauth',
    'allauth.account',
     # 'allauth.socialaccount',

    # GeoNode
    # 'geonode',
)

OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken"
OAUTH2_PROVIDER_GRANT_MODEL = "oauth2_provider.Grant"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "oauth2_provider.RefreshToken"

INSTALLED_APPS += GEONODE_APPS

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

GRAPPELLI_ADMIN_TITLE = os.getenv('GRAPPELLI_ADMIN_TITLE', 'GeoNode')

# Documents application
try:
    # try to parse python notation, default in dockerized env
    ALLOWED_DOCUMENT_TYPES = ast.literal_eval(os.getenv('ALLOWED_DOCUMENT_TYPES'))
except ValueError:
    # fallback to regular list of values separated with misc chars
    ALLOWED_DOCUMENT_TYPES = [
        'txt', 'log', 'doc', 'docx', 'ods', 'odt', 'sld', 'qml', 'xls', 'xlsx', 'xml',
        'bm', 'bmp', 'dwg', 'dxf', 'fif', 'gif', 'jpg', 'jpe', 'jpeg', 'png', 'tif',
        'tiff', 'pbm', 'odp', 'ppt', 'pptx', 'pdf', 'tar', 'tgz', 'rar', 'gz', '7z',
        'zip', 'aif', 'aifc', 'aiff', 'au', 'mp3', 'mpga', 'wav', 'afl', 'avi', 'avs',
        'fli', 'mp2', 'mp4', 'mpg', 'ogg', 'webm', '3gp', 'flv', 'vdo'
    ] if os.getenv('ALLOWED_DOCUMENT_TYPES') is None \
        else re.split(r' *[,|:|;] *', os.getenv('ALLOWED_DOCUMENT_TYPES'))

MAX_DOCUMENT_SIZE = int(os.getenv('MAX_DOCUMENT_SIZE ', '2'))  # MB

# DOCUMENT_TYPE_MAP and DOCUMENT_MIMETYPE_MAP update enumerations in
# documents/enumerations.py and should only
# need to be uncommented if adding other types
# to settings.ALLOWED_DOCUMENT_TYPES

# DOCUMENT_TYPE_MAP = {}
# DOCUMENT_MIMETYPE_MAP = {}

UNOCONV_ENABLE = ast.literal_eval(os.getenv('UNOCONV_ENABLE', 'False'))

if UNOCONV_ENABLE:
    UNOCONV_EXECUTABLE = os.getenv('UNOCONV_EXECUTABLE', '/usr/bin/unoconv')
    UNOCONV_TIMEOUT = int(os.getenv('UNOCONV_TIMEOUT', 30))  # seconds

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
        'simple': {
            'format': '%(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"], "level": "ERROR", },
        "geonode": {
            "handlers": ["console"], "level": "ERROR", },
        "geonode.qgis_server": {
            "handlers": ["console"], "level": "ERROR", },
        "geoserver-restconfig.catalog": {
            "handlers": ["console"], "level": "ERROR", },
        "owslib": {
            "handlers": ["console"], "level": "ERROR", },
        "pycsw": {
            "handlers": ["console"], "level": "ERROR", },
        "celery": {
            'handlers': ["console"], 'level': 'ERROR', },
    },
}

#
# Test Settings
#
on_travis = ast.literal_eval(os.environ.get('ON_TRAVIS', 'False'))
core_tests = ast.literal_eval(os.environ.get('TEST_RUN_CORE', 'False'))
internal_apps_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTERNAL_APPS', 'False'))
integration_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION', 'False'))
integration_server_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION_SERVER', 'False'))
integration_upload_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION_UPLOAD', 'False'))
integration_monitoring_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION_MONITORING', 'False'))
integration_csw_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION_CSW', 'False'))
integration_bdd_tests = ast.literal_eval(os.environ.get('TEST_RUN_INTEGRATION_BDD', 'False'))
selenium_tests = ast.literal_eval(os.environ.get('TEST_RUN_SELENIUM', 'False'))

# Django 1.11 ParallelTestSuite
TEST_RUNNER_KEEPDB = os.environ.get('TEST_RUNNER_KEEPDB', 0)
TEST_RUNNER_PARALLEL = os.environ.get('TEST_RUNNER_PARALLEL', 1)

# GeoNode test suite
# TEST_RUNNER = 'geonode.tests.suite.runner.DjangoParallelTestSuiteRunner'
# TEST_RUNNER_WORKER_MAX = 3
# TEST_RUNNER_WORKER_COUNT = 'auto'
# TEST_RUNNER_NOT_THREAD_SAFE = None
# TEST_RUNNER_PARENT_TIMEOUT = 10
# TEST_RUNNER_WORKER_TIMEOUT = 10

TEST = 'test' in sys.argv

#
# Customizations to built in Django settings required by GeoNode
#

# Django automatically includes the "templates" dir in all the INSTALLED_APPS.
TEMPLATES = [
    {
        'NAME': 'GeoNode Project Templates',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                # 'geonode.context_processors.resource_urls',
                # 'geonode.geoserver.context_processors.geoserver_urls',
                # 'geonode.themes.context_processors.custom_theme'
            ],
            # Either remove APP_DIRS or remove the 'loaders' option.
            # 'loaders': [
            #      'django.template.loaders.filesystem.Loader',
            #      'django.template.loaders.app_directories.Loader',
            # ],
            'debug': DEBUG,
        },
    },
]

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
    # The setting below makes it possible to serve different languages per
    # user depending on things like headers in HTTP requests.
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'geonode.base.middleware.MaintenanceMiddleware',
    # 'geonode.base.middleware.ReadOnlyMiddleware',   # a Middleware enabling Read Only mode of Geonode
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Security stuff
SESSION_EXPIRED_CONTROL_ENABLED = ast.literal_eval(os.environ.get('SESSION_EXPIRED_CONTROL_ENABLED', 'True'))

if SESSION_EXPIRED_CONTROL_ENABLED:
    # This middleware checks for ACCESS_TOKEN validity and if expired forces
    # user logout
    MIDDLEWARE += \
            ('geonode.security.middleware.SessionControlMiddleware',)

SESSION_COOKIE_SECURE = ast.literal_eval(os.environ.get('SESSION_COOKIE_SECURE', 'False'))
CSRF_COOKIE_SECURE = ast.literal_eval(os.environ.get('CSRF_COOKIE_SECURE', 'False'))
CSRF_COOKIE_HTTPONLY = ast.literal_eval(os.environ.get('CSRF_COOKIE_HTTPONLY', 'False'))
CORS_ORIGIN_ALLOW_ALL = ast.literal_eval(os.environ.get('CORS_ORIGIN_ALLOW_ALL', 'False'))
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'DENY')
SECURE_CONTENT_TYPE_NOSNIFF = ast.literal_eval(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', 'True'))
SECURE_BROWSER_XSS_FILTER = ast.literal_eval(os.environ.get('SECURE_BROWSER_XSS_FILTER', 'True'))
SECURE_SSL_REDIRECT = ast.literal_eval(os.environ.get('SECURE_SSL_REDIRECT', 'False'))
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = ast.literal_eval(os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True'))

# Replacement of the default authentication backend in order to support
# permissions per object.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

if 'announcements' in INSTALLED_APPS:
    AUTHENTICATION_BACKENDS += (
        'announcements.auth_backends.AnnouncementPermissionsBackend',
    )

# 1 day expiration time by default
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS', '86400'))

# Require users to authenticate before using Geonode
LOCKDOWN_GEONODE = ast.literal_eval(os.getenv('LOCKDOWN_GEONODE', 'False'))

# Add additional paths (as regular expressions) that don't require
# authentication.
# - authorized exempt urls needed for oauth when GeoNode is set to lockdown
AUTH_EXEMPT_URLS = (
    r'^%s/?$' % FORCE_SCRIPT_NAME,
    '%s/o/*' % FORCE_SCRIPT_NAME,
    '%s/gs/*' % FORCE_SCRIPT_NAME,
    '%s/account/*' % FORCE_SCRIPT_NAME,
    '%s/static/*' % FORCE_SCRIPT_NAME,
    '%s/api/o/*' % FORCE_SCRIPT_NAME,
    '%s/api/roles' % FORCE_SCRIPT_NAME,
    '%s/api/adminRole' % FORCE_SCRIPT_NAME,
    '%s/api/users' % FORCE_SCRIPT_NAME,
    # '%s/api/layers' % FORCE_SCRIPT_NAME,
    # '%s/monitoring' % FORCE_SCRIPT_NAME,
    r'^/i18n/setlang/?$',
)

ANONYMOUS_USER_ID = os.getenv('ANONYMOUS_USER_ID', '-1')
GUARDIAN_GET_INIT_ANONYMOUS_USER = os.getenv(
    'GUARDIAN_GET_INIT_ANONYMOUS_USER',
    'geonode.people.models.get_anonymous_user_instance'
)

# Whether the uplaoded resources should be public and downloadable by default
# or not
DEFAULT_ANONYMOUS_VIEW_PERMISSION = ast.literal_eval(
    os.getenv('DEFAULT_ANONYMOUS_VIEW_PERMISSION', 'True')
)
DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION = ast.literal_eval(
    os.getenv('DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION', 'True')
)

#
# Settings for default search size
#
DEFAULT_SEARCH_SIZE = int(os.getenv('DEFAULT_SEARCH_SIZE', '10'))


#
# Settings for third party apps
#


# Email for users to contact admins.
THEME_ACCOUNT_CONTACT_EMAIL = os.getenv(
    'THEME_ACCOUNT_CONTACT_EMAIL', 'admin@example.com'
)

#
# GeoNode specific settings
#
# per-deployment settings should go here

# Login and logout urls override
LOGIN_URL = os.getenv('LOGIN_URL', '{}account/login/'.format(SITEURL))
LOGOUT_URL = os.getenv('LOGOUT_URL', '{}account/logout/'.format(SITEURL))

ACCOUNT_LOGIN_REDIRECT_URL = os.getenv('LOGIN_REDIRECT_URL', SITEURL)
ACCOUNT_LOGOUT_REDIRECT_URL = os.getenv('LOGOUT_REDIRECT_URL', SITEURL)

# Backend
DEFAULT_WORKSPACE = os.getenv('DEFAULT_WORKSPACE', 'geonode')
CASCADE_WORKSPACE = os.getenv('CASCADE_WORKSPACE', 'geonode')

OGP_URL = os.getenv('OGP_URL', "http://geodata.tufts.edu/solr/select")

# Topic Categories list should not be modified (they are ISO). In case you
# absolutely need it set to True this variable
MODIFY_TOPICCATEGORY = ast.literal_eval(os.getenv('MODIFY_TOPICCATEGORY', 'True'))

# If this option is enabled, Topic Categories will become strictly Mandatory on
# Metadata Wizard
TOPICCATEGORY_MANDATORY = ast.literal_eval(os.environ.get('TOPICCATEGORY_MANDATORY', 'False'))

MISSING_THUMBNAIL = os.getenv(
    'MISSING_THUMBNAIL', 'geonode/img/missing_thumb.png'
)

GEOSERVER_LOCATION = os.getenv(
    'GEOSERVER_LOCATION', 'http://localhost:8080/geoserver/'
)

GEOSERVER_PUBLIC_SCHEMA = os.getenv(
    'GEOSERVER_PUBLIC_SCHEMA', SITE_HOST_SCHEMA
)

GEOSERVER_PUBLIC_HOST = os.getenv(
    'GEOSERVER_PUBLIC_HOST', SITE_HOST_NAME
)

GEOSERVER_PUBLIC_PORT = os.getenv(
    'GEOSERVER_PUBLIC_PORT', 8080
)

_default_public_location = '{}://{}:{}/geoserver/'.format(
    GEOSERVER_PUBLIC_SCHEMA,
    GEOSERVER_PUBLIC_HOST,
    GEOSERVER_PUBLIC_PORT) if GEOSERVER_PUBLIC_PORT else '{}://{}/geoserver/'.format(GEOSERVER_PUBLIC_SCHEMA, GEOSERVER_PUBLIC_HOST)

GEOSERVER_PUBLIC_LOCATION = os.getenv(
    'GEOSERVER_PUBLIC_LOCATION', _default_public_location
)

GEOSERVER_WEB_UI_LOCATION = os.getenv(
    'GEOSERVER_WEB_UI_LOCATION', GEOSERVER_PUBLIC_LOCATION
)

OGC_SERVER_DEFAULT_USER = os.getenv(
    'GEOSERVER_ADMIN_USER', 'admin'
)

OGC_SERVER_DEFAULT_PASSWORD = os.getenv(
    'GEOSERVER_ADMIN_PASSWORD', 'geoserver'
)

USE_GEOSERVER = False

# Uploader Settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

EPSG_CODE_MATCHES = {
    'EPSG:4326': '(4326) WGS 84',
    'EPSG:900913': '(900913) Google Maps Global Mercator',
    'EPSG:3857': '(3857) WGS 84 / Pseudo-Mercator',
    'EPSG:3785': '(3785 DEPRECATED) Popular Visualisation CRS / Mercator',
    'EPSG:32647': '(32647) WGS 84 / UTM zone 47N',
    'EPSG:32736': '(32736) WGS 84 / UTM zone 36S'
}

# CSW settings
CATALOGUE = {
    'default': {
        # The underlying CSW implementation
        # default is pycsw in local mode (tied directly to GeoNode Django DB)
        'ENGINE': 'geonode.catalogue.backends.pycsw_local',
        # pycsw in non-local mode
        # 'ENGINE': 'geonode.catalogue.backends.pycsw_http',
        # GeoNetwork opensource
        # 'ENGINE': 'geonode.catalogue.backends.geonetwork',
        # deegree and others
        # 'ENGINE': 'geonode.catalogue.backends.generic',

        # The FULLY QUALIFIED base url to the CSW instance for this GeoNode
        'URL': urljoin(SITEURL, '/catalogue/csw'),
        # 'URL': 'http://localhost:8080/geonetwork/srv/en/csw',
        # 'URL': 'http://localhost:8080/deegree-csw-demo-3.0.4/services',

        # login credentials (for GeoNetwork)
        # 'USER': 'admin',
        # 'PASSWORD': 'admin',

        # 'ALTERNATES_ONLY': True,
    }
}

_DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S.%f %Z', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S%Z']
DATETIME_INPUT_FORMATS = DATETIME_INPUT_FORMATS + _DATETIME_INPUT_FORMATS

# DISPLAY_SOCIAL = ast.literal_eval(os.getenv('DISPLAY_SOCIAL', 'True'))
# DISPLAY_COMMENTS = ast.literal_eval(os.getenv('DISPLAY_COMMENTS', 'True'))
# DISPLAY_RATINGS = ast.literal_eval(os.getenv('DISPLAY_RATINGS', 'True'))
# DISPLAY_WMS_LINKS = ast.literal_eval(os.getenv('DISPLAY_WMS_LINKS', 'True'))
#
# SOCIAL_ORIGINS = [{
#     "label": "Email",
#     "url": "mailto:?subject={name}&body={url}",
#     "css_class": "email"
# }, {
#     "label": "Facebook",
#     "url": "http://www.facebook.com/sharer.php?u={url}",
#     "css_class": "fb"
# }, {
#     "label": "Twitter",
#     "url": "https://twitter.com/share?url={url}&hashtags={hashtags}",
#     "css_class": "tw"
# }]

# CKAN Query String Parameters names pulled from
# http://tinyurl.com/og2jofn
CKAN_ORIGINS = [{
    "label": "Humanitarian Data Exchange (HDX)",
    "url": "https://data.hdx.rwlabs.org/dataset/new?title={name}&"
    "dataset_date={date}&notes={abstract}&caveats={caveats}",
    "css_class": "hdx"
}]
# SOCIAL_ORIGINS.extend(CKAN_ORIGINS)

# Setting TWITTER_CARD to True will enable Twitter Cards
# https://dev.twitter.com/cards/getting-started
# Be sure to replace @GeoNode with your organization or site's twitter handle.
TWITTER_CARD = ast.literal_eval(os.getenv('TWITTER_CARD', 'True'))
TWITTER_SITE = '@GeoNode'
TWITTER_HASHTAGS = ['geonode']

OPENGRAPH_ENABLED = ast.literal_eval(os.getenv('OPENGRAPH_ENABLED', 'True'))

# Enable Licenses User Interface
# Regardless of selection, license field stil exists as a field in the
# Resourcebase model.
# Detail Display: above, below, never
# Metadata Options: verbose, light, never
LICENSES = {
    'ENABLED': True,
    'DETAIL': 'above',
    'METADATA': 'verbose',
}

SRID = {
    'DETAIL': 'never',
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

try:
    # try to parse python notation, default in dockerized env
    ALLOWED_HOSTS = ast.literal_eval(os.getenv('ALLOWED_HOSTS'))
except ValueError:
    # fallback to regular list of values separated with misc chars
    ALLOWED_HOSTS = [HOSTNAME, 'localhost', 'django', 'geonode'] if os.getenv('ALLOWED_HOSTS') is None \
        else re.split(r' *[,|:|;] *', os.getenv('ALLOWED_HOSTS'))

# AUTH_IP_WHITELIST property limits access to users/groups REST endpoints
# to only whitelisted IP addresses.
#
# Empty list means 'allow all'
#
# If you need to limit 'api' REST calls to only some specific IPs
# fill the list like below:
#
# AUTH_IP_WHITELIST = ['192.168.1.158', '192.168.1.159']
AUTH_IP_WHITELIST = [HOSTNAME, 'localhost', 'django', 'geonode'] if os.getenv('AUTH_IP_WHITELIST') is None \
        else re.split(r' *[,|:|;] *', os.getenv('AUTH_IP_WHITELIST'))

# A tuple of hosts the proxy can send requests to.
try:
    # try to parse python notation, default in dockerized env
    PROXY_ALLOWED_HOSTS = ast.literal_eval(os.getenv('PROXY_ALLOWED_HOSTS'))
except ValueError:
    # fallback to regular list of values separated with misc chars
    PROXY_ALLOWED_HOSTS = [HOSTNAME, 'localhost', 'django', 'geonode', 'spatialreference.org', 'nominatim.openstreetmap.org', 'dev.openlayers.org'] if os.getenv('PROXY_ALLOWED_HOSTS') is None \
        else re.split(r' *[,|:|;] *', os.getenv('PROXY_ALLOWED_HOSTS'))

# The proxy to use when making cross origin requests.
PROXY_URL = os.environ.get('PROXY_URL', '/proxy/?url=')

# Haystack Search Backend Configuration. To enable,
# first install the following:
# - pip install django-haystack
# - pip install pyelasticsearch
# Set HAYSTACK_SEARCH to True
# Run "python manage.py rebuild_index"
HAYSTACK_SEARCH = ast.literal_eval(os.getenv('HAYSTACK_SEARCH', 'False'))
# Avoid permissions prefiltering
SKIP_PERMS_FILTER = ast.literal_eval(os.getenv('SKIP_PERMS_FILTER', 'False'))
# Update facet counts from Haystack
HAYSTACK_FACET_COUNTS = ast.literal_eval(os.getenv('HAYSTACK_FACET_COUNTS', 'True'))
if HAYSTACK_SEARCH:
    if 'haystack' not in INSTALLED_APPS:
        INSTALLED_APPS += ('haystack', )
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
            'URL': os.getenv('HAYSTACK_ENGINE_URL', 'http://127.0.0.1:9200/'),
            'INDEX_NAME': os.getenv('HAYSTACK_ENGINE_INDEX_NAME', 'haystack'),
        },
    }
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    HAYSTACK_SEARCH_RESULTS_PER_PAGE = int(os.getenv('HAYSTACK_SEARCH_RESULTS_PER_PAGE', '200'))

DISPLAY_ORIGINAL_DATASET_LINK = ast.literal_eval(
    os.getenv('DISPLAY_ORIGINAL_DATASET_LINK', 'True'))

ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = ast.literal_eval(
    os.getenv('ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE', 'False'))

# gravatar settings
AUTO_GENERATE_AVATAR_SIZES = (
    20, 30, 32, 40, 50, 65, 70, 80, 100, 140, 200, 240
)
AVATAR_GRAVATAR_SSL = ast.literal_eval(os.getenv('AVATAR_GRAVATAR_SSL', 'False'))

AVATAR_DEFAULT_URL = os.getenv('AVATAR_DEFAULT_URL', '/geonode/img/avatar.png')

try:
    # try to parse python notation, default in dockerized env
    AVATAR_PROVIDERS = ast.literal_eval(os.getenv('AVATAR_PROVIDERS'))
except ValueError:
    # fallback to regular list of values separated with misc chars
    AVATAR_PROVIDERS = (
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.GravatarAvatarProvider',
    'avatar.providers.DefaultAvatarProvider'
   ) if os.getenv('AVATAR_PROVIDERS') is None \
        else re.split(r' *[,|:|;] *', os.getenv('AVATAR_PROVIDERS'))

# Number of results per page listed in the GeoNode search pages
CLIENT_RESULTS_LIMIT = int(os.getenv('CLIENT_RESULTS_LIMIT', '5'))

# LOCKDOWN API endpoints to prevent unauthenticated access.
# If set to True, search won't deliver results and filtering ResourceBase-objects is not possible for anonymous users
API_LOCKDOWN = ast.literal_eval(
    os.getenv('API_LOCKDOWN', 'False'))

# Number of items returned by the apis 0 equals no limit
API_LIMIT_PER_PAGE = int(os.getenv('API_LIMIT_PER_PAGE', '200'))
API_INCLUDE_REGIONS_COUNT = ast.literal_eval(
    os.getenv('API_INCLUDE_REGIONS_COUNT', 'False'))

# Settings for CREATE_LAYER plugin
CREATE_LAYER = ast.literal_eval(os.getenv('CREATE_LAYER', 'False'))

if CREATE_LAYER:
    if 'geonode.geoserver.createlayer' not in INSTALLED_APPS:
        INSTALLED_APPS += ('geonode.geoserver.createlayer',)

# Settings for FAVORITE plugin
# FAVORITE_ENABLED = ast.literal_eval(os.getenv('FAVORITE_ENABLED', 'True'))
#
# if FAVORITE_ENABLED:
#     if 'geonode.favorite' not in INSTALLED_APPS:
#         INSTALLED_APPS += ('geonode.favorite',)


# Settings for RECAPTCHA plugin
RECAPTCHA_ENABLED = ast.literal_eval(os.environ.get('RECAPTCHA_ENABLED', 'False'))

if RECAPTCHA_ENABLED:
    if 'captcha' not in INSTALLED_APPS:
        INSTALLED_APPS += ('captcha',)
    ACCOUNT_SIGNUP_FORM_CLASS = os.getenv("ACCOUNT_SIGNUP_FORM_CLASS",
                                          'geonode.people.forms.AllauthReCaptchaSignupForm')
    """
     In order to generate reCaptcha keys, please see:
      - https://pypi.org/project/django-recaptcha/#installation
      - https://pypi.org/project/django-recaptcha/#local-development-and-functional-testing
    """
    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY", 'geonode_RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY", 'geonode_RECAPTCHA_PRIVATE_KEY')

GEONODE_CATALOGUE_METADATA_XSL = ast.literal_eval(os.getenv('GEONODE_CATALOGUE_METADATA_XSL', 'True'))

# -- START Client Hooksets Setup

# GeoNode javascript client configuration

# default map projection
# Note: If set to EPSG:4326, then only EPSG:4326 basemaps will work.
DEFAULT_MAP_CRS = os.environ.get('DEFAULT_MAP_CRS', "EPSG:3857")

DEFAULT_LAYER_FORMAT = os.environ.get('DEFAULT_LAYER_FORMAT', "image/png")

# Where should newly created maps be focused?
DEFAULT_MAP_CENTER = (os.environ.get('DEFAULT_MAP_CENTER_X', 0), os.environ.get('DEFAULT_MAP_CENTER_Y', 0))

# How tightly zoomed should newly created maps be?
# 0 = entire world;
# maximum zoom is between 12 and 15 (for Google Maps, coverage varies by area)
DEFAULT_MAP_ZOOM = int(os.environ.get('DEFAULT_MAP_ZOOM', 0))

MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN', None)
BING_API_KEY = os.environ.get('BING_API_KEY', None)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', None)

GEONODE_CLIENT_LAYER_PREVIEW_LIBRARY = os.getenv('GEONODE_CLIENT_LAYER_PREVIEW_LIBRARY', 'mapstore')

MAP_BASELAYERS = [{}]

# -- END Client Hooksets Setup

SERVICE_UPDATE_INTERVAL = 0

SEARCH_FILTERS = {
    'TEXT_ENABLED': True,
    'TYPE_ENABLED': True,
    'CATEGORIES_ENABLED': True,
    'OWNERS_ENABLED': True,
    'KEYWORDS_ENABLED': True,
    'H_KEYWORDS_ENABLED': True,
    'T_KEYWORDS_ENABLED': True,
    'DATE_ENABLED': True,
    'REGION_ENABLED': True,
    'EXTENT_ENABLED': True,
    'GROUPS_ENABLED': True,
    'GROUP_CATEGORIES_ENABLED': True,
}

# Make Free-Text Kaywords writable from users or read-only
# - if True only admins can edit free-text kwds from admin dashboard
FREETEXT_KEYWORDS_READONLY = ast.literal_eval(os.environ.get('FREETEXT_KEYWORDS_READONLY', 'False'))

# ########################################################################### #
# ASYNC SETTINGS
# ########################################################################### #
# async signals can be the same as broker url
# but they should have separate setting anyway
# use amqp://localhost for local rabbitmq server
"""
    sudo apt-get install -y erlang
    sudo apt-get install rabbitmq-server

    sudo update-rc.d rabbitmq-server enable

    sudo rabbitmqctl stop_app
    sudo rabbitmqctl reset
    sudo rabbitmqctl start_app

    sudo rabbitmqctl list_queues
"""
# Disabling the heartbeat because workers seems often disabled in flower,
# thanks to http://stackoverflow.com/a/14831904/654755
BROKER_HEARTBEAT = 0

# Avoid long running and retried tasks to be run over-and-over again.
BROKER_TRANSPORT_OPTIONS = {
    'fanout_prefix': True,
    'fanout_patterns': True,
    'socket_timeout': 60,
    'visibility_timeout': 86400
}

ASYNC_SIGNALS = ast.literal_eval(os.environ.get('ASYNC_SIGNALS', 'False'))
RABBITMQ_SIGNALS_BROKER_URL = 'amqp://localhost:5672'
# REDIS_SIGNALS_BROKER_URL = 'redis://localhost:6379/0'
LOCAL_SIGNALS_BROKER_URL = 'memory://'

if ASYNC_SIGNALS:
    _BROKER_URL = RABBITMQ_SIGNALS_BROKER_URL
    CELERY_RESULT_BACKEND = 'rpc://'
else:
    _BROKER_URL = LOCAL_SIGNALS_BROKER_URL
    CELERY_RESULT_BACKEND_PATH = os.getenv(
        'CELERY_RESULT_BACKEND_PATH', os.path.join(PROJECT_ROOT, '.celery_results'))
    if not os.path.exists(CELERY_RESULT_BACKEND_PATH):
        os.makedirs(CELERY_RESULT_BACKEND_PATH)
    CELERY_RESULT_BACKEND = 'file:///%s' % CELERY_RESULT_BACKEND_PATH

CELERY_BROKER_URL = os.environ.get('BROKER_URL', _BROKER_URL)
CELERY_RESULT_PERSISTENT = ast.literal_eval(os.environ.get('CELERY_RESULT_PERSISTENT', 'True'))

# Allow to recover from any unknown crash.
CELERY_ACKS_LATE = ast.literal_eval(os.environ.get('CELERY_ACKS_LATE', 'True'))

# Set this to False in order to run async
_EAGER_FLAG = 'False' if ASYNC_SIGNALS else 'True'
CELERY_TASK_ALWAYS_EAGER = ast.literal_eval(os.environ.get('CELERY_TASK_ALWAYS_EAGER', _EAGER_FLAG))
CELERY_TASK_EAGER_PROPAGATES = ast.literal_eval(os.environ.get('CELERY_TASK_EAGER_PROPAGATES', 'True'))

# I use these to debug kombu crashes; we get a more informative message.
CELERY_TASK_SERIALIZER = os.environ.get('CELERY_TASK_SERIALIZER', 'json')
CELERY_RESULT_SERIALIZER = os.environ.get('CELERY_RESULT_SERIALIZER', 'json')
CELERY_ACCEPT_CONTENT = [CELERY_RESULT_SERIALIZER, ]

# Set Tasks Queues
# CELERY_TASK_DEFAULT_QUEUE = "default"
# CELERY_TASK_DEFAULT_EXCHANGE = "default"
# CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
# CELERY_TASK_DEFAULT_ROUTING_KEY = "default"
CELERY_TASK_CREATE_MISSING_QUEUES = ast.literal_eval(os.environ.get('CELERY_TASK_CREATE_MISSING_QUEUES', 'True'))
GEONODE_EXCHANGE = Exchange("default", type="direct", durable=True)
GEOSERVER_EXCHANGE = Exchange("geonode", type="topic", durable=False)
CELERY_TASK_QUEUES = (
    Queue('default', GEONODE_EXCHANGE, routing_key='default', priority=0),
    Queue('geonode', GEONODE_EXCHANGE, routing_key='geonode', priority=0),
    Queue('update', GEONODE_EXCHANGE, routing_key='update', priority=0),
    Queue('cleanup', GEONODE_EXCHANGE, routing_key='cleanup', priority=0),
    Queue('email', GEONODE_EXCHANGE, routing_key='email', priority=0),
)

if USE_GEOSERVER:
    CELERY_TASK_QUEUES += (
        Queue("broadcast", GEOSERVER_EXCHANGE, routing_key="#"),
        Queue("email.events", GEOSERVER_EXCHANGE, routing_key="email"),
        Queue("all.geoserver", GEOSERVER_EXCHANGE, routing_key="geoserver.#"),
        Queue("geoserver.catalog", GEOSERVER_EXCHANGE, routing_key="geoserver.catalog"),
        Queue("geoserver.data", GEOSERVER_EXCHANGE, routing_key="geoserver.catalog"),
        Queue("geoserver.events", GEOSERVER_EXCHANGE, routing_key="geonode.geoserver"),
        Queue("notifications.events", GEOSERVER_EXCHANGE, routing_key="notifications"),
        Queue("geonode.layer.viewer", GEOSERVER_EXCHANGE, routing_key="geonode.viewer"),
    )

# from celery.schedules import crontab
# EXAMPLES
#     ...
#     'update_feeds': {
#         'task': 'arena.social.tasks.Update',
#         'schedule': crontab(minute='*/6'),
#     },
#     ...
#     'send-summary-every-hour': {
#        'task': 'summary',
#         # There are 4 ways we can handle time, read further
#        'schedule': 3600.0,
#         # If you're using any arguments
#        'args': (‘We don’t need any’,),
#     },
#     # Executes every Friday at 4pm
#     'send-notification-on-friday-afternoon': {
#          'task': 'my_app.tasks.send_notification',
#          'schedule': crontab(hour=16, day_of_week=5),
#     },
CELERY_BEAT_SCHEDULE = {}

# if 'geonode.services' in INSTALLED_APPS:
#     CELERY_BEAT_SCHEDULE['probe_services'] = {
#         'task': 'geonode.services.tasks.probe_services',
#         'schedule': 600.0,
#     }

DELAYED_SECURITY_SIGNALS = ast.literal_eval(os.environ.get('DELAYED_SECURITY_SIGNALS', 'False'))
CELERY_ENABLE_UTC = ast.literal_eval(os.environ.get('CELERY_ENABLE_UTC', 'True'))
CELERY_TIMEZONE = TIME_ZONE

# Half a day is enough
CELERY_TASK_RESULT_EXPIRES = os.environ.get('CELERY_TASK_RESULT_EXPIRES', 43200)

# Sometimes, Ask asks us to enable this to debug issues.
# BTW, it will save some CPU cycles.
CELERY_DISABLE_RATE_LIMITS = ast.literal_eval(os.environ.get('CELERY_DISABLE_RATE_LIMITS', 'False'))
CELERY_SEND_TASK_EVENTS = ast.literal_eval(os.environ.get('CELERY_SEND_TASK_EVENTS', 'True'))
CELERY_WORKER_DISABLE_RATE_LIMITS = ast.literal_eval(os.environ.get('CELERY_WORKER_DISABLE_RATE_LIMITS', 'False'))
CELERY_WORKER_SEND_TASK_EVENTS = ast.literal_eval(os.environ.get('CELERY_WORKER_SEND_TASK_EVENTS', 'True'))

# Allow our remote workers to get tasks faster if they have a
# slow internet connection (yes Gurney, I'm thinking of you).
CELERY_MESSAGE_COMPRESSION = os.environ.get('CELERY_MESSAGE_COMPRESSION', 'gzip')

# The default beiing 5000, we need more than this.
CELERY_MAX_CACHED_RESULTS = os.environ.get('CELERY_MAX_CACHED_RESULTS', 32768)

# NOTE: I don't know if this is compatible with upstart.
CELERYD_POOL_RESTARTS = ast.literal_eval(os.environ.get('CELERYD_POOL_RESTARTS', 'True'))
CELERY_SEND_TASK_SENT_EVENT = ast.literal_eval(os.environ.get('CELERY_SEND_TASK_SENT_EVENT', 'True'))

# Disabled by default and I like it, because we use Sentry for this.
CELERY_SEND_TASK_ERROR_EMAILS = ast.literal_eval(os.environ.get('CELERY_SEND_TASK_ERROR_EMAILS', 'False'))

# ########################################################################### #
# NOTIFICATIONS SETTINGS
# ########################################################################### #
NOTIFICATION_ENABLED = ast.literal_eval(os.environ.get('NOTIFICATION_ENABLED', 'True')) or TEST
#PINAX_NOTIFICATIONS_LANGUAGE_MODEL = "people.Profile"

# notifications backends
NOTIFICATIONS_BACKEND = os.environ.get('NOTIFICATIONS_BACKEND', 'geonode.notifications_backend.EmailBackend')
PINAX_NOTIFICATIONS_BACKENDS = [
    ("email", NOTIFICATIONS_BACKEND, 0),
]
PINAX_NOTIFICATIONS_HOOKSET = "pinax.notifications.hooks.DefaultHookSet"

# Queue non-blocking notifications.
# Set this to False in order to run async
_QUEUE_ALL_FLAG = 'True' if ASYNC_SIGNALS else 'False'
PINAX_NOTIFICATIONS_QUEUE_ALL = ast.literal_eval(os.environ.get('NOTIFICATIONS_QUEUE_ALL', _QUEUE_ALL_FLAG))
PINAX_NOTIFICATIONS_LOCK_WAIT_TIMEOUT = os.environ.get('NOTIFICATIONS_LOCK_WAIT_TIMEOUT', 600)

# explicitly define NOTIFICATION_LOCK_LOCATION
# NOTIFICATION_LOCK_LOCATION = <path>


# ########################################################################### #
# SECURITY SETTINGS
# ########################################################################### #

# Require users to authenticate before using Geonode
if LOCKDOWN_GEONODE:
    MIDDLEWARE += \
        ('geonode.security.middleware.LoginRequiredMiddleware',)

# for windows users check if they didn't set GEOS and GDAL in local_settings.py
# maybe they set it as a windows environment
if os.name == 'nt':
    if "GEOS_LIBRARY_PATH" not in locals() \
            or "GDAL_LIBRARY_PATH" not in locals():
        if os.environ.get("GEOS_LIBRARY_PATH", None) \
                and os.environ.get("GDAL_LIBRARY_PATH", None):
            GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
            GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
        else:
            # maybe it will be found regardless if not it will throw 500 error
            from django.contrib.gis.geos import GEOSGeometry  # flake8: noqa

# Keywords thesauri
# e.g. THESAURUS = {'name':'inspire_themes', 'required':True, 'filter':True}
# Required: (boolean, optional, default false) mandatory while editing metadata (not implemented yet)
# Filter: (boolean, optional, default false) a filter option on that thesaurus will appear in the main search page
# THESAURUS = {'name': 'inspire_themes', 'required': True, 'filter': True}

# ######################################################## #
# Advanced Resource Publishing Worklow Settings - START    #
# ######################################################## #
"""
    - if [ RESOURCE_PUBLISHING == True ]
      1. "unpublished" won't be visibile to Anonymous users
      2. "unpublished" will be visible to registered users **IF** they have view permissions
      3. "unpublished" will be always visible to the owner and Group Managers
      By default the uploaded resources will be "unpublished".
      The owner will be able to change them to "published" **UNLESS** the ADMIN_MODERATE_UPLOADS is activated.
      If the owner assigns unpublished resources to a Group, both from Metadata and Permissions, in any case
       the Group "Managers" will be able to edit the Resource.

    - if [ ADMIN_MODERATE_UPLOADS == True ]
      1. The owner won't be able to change to neither "approved" nor "published" state (unless he is a superuser)
      2. If the Resource belongs to a Group somehow, the Managers will be able to change the state to "approved"
         but **NOT** to "published". Only a superuser can publish a resource.
      3. Superusers can do enything.

    - if [ GROUP_PRIVATE_RESOURCES == True ]
      The "unapproved" and "unpublished" Resources will be accessible **ONLY** by owners, superusers and member of 
       the belonging groups.

    - if [ GROUP_MANDATORY_RESOURCES == True ]
      Editor will be **FORCED** to select a Group when editing the resource metadata.
"""

# option to enable/disable resource unpublishing for administrators and members
RESOURCE_PUBLISHING = ast.literal_eval(os.getenv('RESOURCE_PUBLISHING', 'False'))

# Each uploaded Layer must be approved by an Admin before becoming visible
ADMIN_MODERATE_UPLOADS = ast.literal_eval(os.environ.get('ADMIN_MODERATE_UPLOADS', 'False'))

# If this option is enabled, Resources belonging to a Group (with access private) won't be
# visible by others
GROUP_PRIVATE_RESOURCES = ast.literal_eval(os.environ.get('GROUP_PRIVATE_RESOURCES', 'False'))

# If this option is enabled, Groups will become strictly Mandatory on
# Metadata Wizard
GROUP_MANDATORY_RESOURCES = ast.literal_eval(os.environ.get('GROUP_MANDATORY_RESOURCES', 'False'))
# ######################################################## #
# Advanced Resource Publishing Worklow Settings - END      #
# ######################################################## #

# A boolean which specifies wether to display the email in user's profile
SHOW_PROFILE_EMAIL = ast.literal_eval(os.environ.get('SHOW_PROFILE_EMAIL', 'False'))

# Enables cross origin requests for geonode-client
MAP_CLIENT_USE_CROSS_ORIGIN_CREDENTIALS = ast.literal_eval(os.getenv(
    'MAP_CLIENT_USE_CROSS_ORIGIN_CREDENTIALS',
    'False'
))

ACCOUNT_OPEN_SIGNUP = ast.literal_eval(os.environ.get('ACCOUNT_OPEN_SIGNUP', 'True'))
ACCOUNT_APPROVAL_REQUIRED = ast.literal_eval(
    os.getenv('ACCOUNT_APPROVAL_REQUIRED', 'False')
)
ACCOUNT_ADAPTER = 'geonode.people.adapters.LocalAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = os.environ.get('ACCOUNT_AUTHENTICATION_METHOD', 'username_email')
ACCOUNT_CONFIRM_EMAIL_ON_GET = ast.literal_eval(os.environ.get('ACCOUNT_CONFIRM_EMAIL_ON_GET', 'True'))
ACCOUNT_EMAIL_REQUIRED = ast.literal_eval(os.environ.get('ACCOUNT_EMAIL_REQUIRED', 'True'))
ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'none')

# Since django-allauth 0.43.0.
ACCOUNT_SIGNUP_REDIRECT_URL = os.environ.get('ACCOUNT_SIGNUP_REDIRECT_URL', os.getenv('SITEURL', _default_siteurl))
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = int(os.getenv('ACCOUNT_LOGIN_ATTEMPTS_LIMIT', '3'))
ACCOUNT_MAX_EMAIL_ADDRESSES = int(os.getenv('ACCOUNT_MAX_EMAIL_ADDRESSES', '2'))

INVITATIONS_ADAPTER = ACCOUNT_ADAPTER

# Choose thumbnail generator -- this is the default generator
THUMBNAIL_GENERATOR = "geonode.layers.utils.create_gs_thumbnail_geonode"
#THUMBNAIL_GENERATOR_DEFAULT_BG = r"http://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
THUMBNAIL_GENERATOR_DEFAULT_BG = r"https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png"
THUMBNAIL_GENERATOR_DEFAULT_SIZE = {'width': 240, 'height': 200}

USER_ANALYTICS_ENABLED = ast.literal_eval(os.getenv('USER_ANALYTICS_ENABLED', 'False'))
USER_ANALYTICS_GZIP = ast.literal_eval(os.getenv('USER_ANALYTICS_GZIP', 'False'))

GEOIP_PATH = os.getenv('GEOIP_PATH', os.path.join(PROJECT_ROOT, 'GeoIPCities.dat'))
SEARCH_RESOURCES_EXTENDED = strtobool(os.getenv('SEARCH_RESOURCES_EXTENDED', 'True'))
# -- END Settings for MONITORING plugin

