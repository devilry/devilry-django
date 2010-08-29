# vim: ft=python

import os
import sys

# Add the python libraries to the path
sys.path.append('/uio/arkimedes/s11/espeak/devilry/django') # django
sys.path.append('/uio/arkimedes/s11/espeak/devilry/devilry-django') # devilry

# Select which settings to use
os.environ['DJANGO_SETTINGS_MODULE'] = 'devilry.settings_production'

# Create the django wsgi application
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
