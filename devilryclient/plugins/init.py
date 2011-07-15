#!/usr/bin/env python

import sys, os, logging, ConfigParser
from os.path import dirname, abspath, join
from devilryclient.utils import logging_startup

args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args

if len(otherargs) < 2:
    logging.warning('Not enough input arguments!')
    logging.warning('Usage: init url filename')
    sys.exit(0)

url = otherargs[0]
#TODO check that url is gyldig devilry url

name = otherargs[1]

Config = ConfigParser.ConfigParser()

dirpath = join(os.getcwd(), name)
devdirpath = join(dirpath, '.devilry')
try:
    os.mkdir(dirpath)
    os.mkdir(devdirpath)
    cfgfile = open(join(devdirpath, 'config'), 'w')
except OSError:
    print logging.warning('Could not setup because directory already exists')
    raise SystemExit()

Config.add_section('URL')
Config.set('URL', 'url', '{}'.format(url))
Config.add_section('devilrydir')
Config.set('devilrydir', 'path', '{}'.format(dirpath))

Config.write(cfgfile)
cfgfile.close()



