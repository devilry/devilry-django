#!/usr/bin/env python

import sys, os, logging
from os.path import dirname, abspath, join
from utils import logging_startup

args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args

url = otherargs[0]
#TODO check that url is gyldig devilry url

dirname = otherargs[1]

dirpath = join(os.getcwd(), dirname)
devdirpath = join(dirpath, '.devilry')
try:
    os.mkdir(dirpath)
    os.mkdir(devdirpath)
    config = open(join(devdirpath, 'config'), 'w')
except OSError:
    print logging.warning('Could not setup because direcory already exists')
    raise SystemExit()

#write url and filename to config

#put in config file



#ta inn url og mappenavn. legge i config fil
#lage mappe i mappen den kjores fra
