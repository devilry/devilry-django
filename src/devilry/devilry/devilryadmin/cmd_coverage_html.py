#!/usr/bin/env python
# Check test coverage and create a html-report of the results

from common import depends, Command, require_djangoproject, getcwd, append_pythonexec_to_command
from subprocess import call
from os.path import join
from sys import argv

htmlout = join(getcwd(), 'coverage_html_report')
require_djangoproject()
depends(Command('coverage', *argv[1:]))

command = ["coverage", "html", "-i", "-d", htmlout]
call(append_pythonexec_to_command(command))
