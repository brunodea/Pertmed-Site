import os, sys
sys.path.append('/home/bruno/Documents/gmob/pertmed_site/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pertmed_site.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

