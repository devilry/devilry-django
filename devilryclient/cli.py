#!/usr/bin/env python

import sys, logging
from utils import execute, logging_startup


command = sys.argv[1]
args = sys.argv[2:]

logging_startup(args)

logging.info('Hello!')
execute(command, args)


