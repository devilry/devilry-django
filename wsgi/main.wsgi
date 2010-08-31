# vim: ft=python

import os
import sys

# Add the python libraries to the path
if not '/devilry/lib/django' in sys.path:
    sys.path.append('/devilry/lib/django') # django
if not '/devilry/lib/devilry-django' in sys.path:
    sys.path.append('/devilry/lib/devilry-django') # devilry

# Select which settings to use
os.environ['DJANGO_SETTINGS_MODULE'] = 'devilry.cfg.prod1'

# Create the django wsgi application
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
