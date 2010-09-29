from os.path import exists, join
import sys
sys.path.append('web')

try:
  from localsettings import * 
except:
  print """You do not appear to have a database setup defined, if you are running this on a development
  environment, then you need to copy localsettings.py.example to localsettings.py and edit it for your personal settings.
  If this message is displayed in a production environment, then it has not been set up correctly."""
  sys.exit()

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-uk'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
MEDIA_DIR = DOMESDAY_DIR + 'media/'
MEDIA_URL = '/media/'
MEDIA_ROOT = URL_ROOT + 'media/'

# URL prefix for admin media -- CSS, JavaScript and images
ADMIN_MEDIA_PREFIX = '/media-admin/'
MEDIA_ADMIN_DIR = DOMESDAY_DIR + 'media-admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hn=nz!e#8@ac2y(wl_-#p7xanhp43jijqm2oi*!@szt4a#s3hu'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "pagination.middleware.PaginationMiddleware",
)

ROOT_URLCONF = 'domesday.urls'

TEMPLATE_DIRS = (
    DOMESDAY_DIR + 'templates/',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.request',
  'domesday.context_processors.site',
  'domesday.context_processors.template_settings',
  'domesday.context_processors.maps_api_key',
  "django.core.context_processors.request",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin', 
    'domesday.domes',
    'contact_form',
    'django.contrib.comments',
    'pagination',
    'django.contrib.gis',
)

# Defaults to MEDIA_URL + 'snapboard/'
SNAP_MEDIA_PREFIX = '/media'
# Set to False if your templates include the SNAPboard login form
USE_SNAPBOARD_LOGIN_FORM = True
# Select your filter, the default is Markdown
# Possible values: 'bbcode', 'markdown', 'textile'
SNAP_POST_FILTER = 'bbcode'
