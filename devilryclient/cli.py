#!/usr/bin/env python

import sys
import logging
from utils import execute, logging_startup, showhelp

try:
    command = sys.argv[1]
    args = sys.argv[2:]
except IndexError:
    showhelp()
    raise SystemExit()

logging_startup(args)

logging.info('Hello!')
execute(command, args)
