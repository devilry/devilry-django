#!/usr/bin/env python
# Build the docs as HTML using sphinx (using make html from docs/)

from common import get_docsdir
import os
from subprocess import call


os.chdir(get_docsdir())
call(['make', 'html'])
