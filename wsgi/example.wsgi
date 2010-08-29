# vim: ft=python

import os
import sys

# Path to the django site
sys.path.append('/mnt/hgfs/code/devilry-django')

# Select which settings to use
os.environ['DJANGO_SETTINGS_MODULE'] = 'devilry.settings_apache_example'

# Create the django wsgi application
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
