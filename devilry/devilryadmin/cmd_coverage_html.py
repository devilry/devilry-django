#!/usr/bin/env python
# Check test coverage and create a html-report of the results

from common import depends, Command, require_djangoproject
from subprocess import call
from sys import argv

require_djangoproject()
depends(Command('coverage', *argv[1:]))

command = ["coverage", "html", "-d", "coverage_html_report"]
call(command)
