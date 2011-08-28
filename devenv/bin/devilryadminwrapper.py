#!/usr/bin/env python

import os
import django_dev
import sys
from devilry.devilryadmin.devilryadmin import cli


# Add the PYTHONPATH set in devmanage to PYTHONPATH so that devilryadmin sub processes have correct path.
os.environ['PYTHONPATH'] = ':'.join(sys.path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'devilry.projects.dev.settings'

# Run devilryadmin
cli()
