#!/usr/bin/env python
# Check test coverage, takes optional parameters for what to test. eg core to run all core-tests

from subprocess import call
import sys

commands = ["coverage", "-x", "../projects/dev/manage.py", "test"]

if len(sys.argv)>1:
    commands.append(sys.argv[1])

call(commands)
