#!/usr/bin/env python
# Check test coverage and create a html-report of the results

from common import depends, Command
from subprocess import call
from sys import argv

depends(Command('coverage', *argv[1:]))

command = ["coverage", "html"]
call(command)
