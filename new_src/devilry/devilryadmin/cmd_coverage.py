#!/usr/bin/env python
# Check test coverage, takes optional parameters for what to test. eg core to run all core-tests

from subprocess import call
from common import require_djangoproject, getcwd, getreporoot, append_pythonexec_to_command
from os.path import join, exists
from os import remove
import sys

def createCoveragerc(crcpath):
    coveragerc = "#automatically created by devilry\n[run]\ninclude = {path!s}/*".format(path=getreporoot())
    coveragercfile = open(crcpath, 'w')
    coveragercfile.write(coveragerc)
    coveragercfile.close()

def checkCoveragerc(crcpath):
    coveragercfile = open(crcpath, 'r')
    line = coveragercfile.readline()
    coveragercfile.close()
    if line == '#automatically created by devilry\n':
        return True
    return False

def runCoverage(crcpath):
    if not exists(crcpath):
        createCoveragerc(crcpath)
    elif not checkCoveragerc(crcpath):
        raise SystemExit('This folder contains a .coveragerc-file not created by Devilry.')

    managepath = join(getcwd(), 'manage.py')
    commands = ["coverage", "run", managepath, "test"]

    if len(sys.argv)>1:
        commands.append(sys.argv[1])
    call(append_pythonexec_to_command(commands))



require_djangoproject()
crcpath = join(getcwd(), '.coveragerc')
runCoverage(crcpath)

if exists(crcpath):
    remove(crcpath)
