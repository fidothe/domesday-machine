# local configurations for your computer
import os
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           
DATABASE_NAME = ''             
DATABASE_USER = ''            
DATABASE_PASSWORD = ''        
DATABASE_HOST = ''             
DATABASE_PORT = ''  

URL_ROOT = '/'           # prefix for URLs to run not at top level of domain
HOME_DIR = '' # the parent directory of DOMESDAY_DIR
DOMESDAY_DIR = HOME_DIR + '/domesday/'      # top level directory of the installation

FEEDBACK_EMAIL = ''
FEEDBACK_EMAIL_TITLE = '[Domesday Feedback]'

EMAIL_HOST = 'localhost'
EMAIL_PORT = '1025'
EMAIL_SUBJECT_PREFIX = "[Domesday Bugs] "

MAPS_API_KEY = ''
