#!/usr/bin/env python

import logging, argparse
from utils import execute, showhelp, logging_startup

parser = argparse.ArgumentParser()
parser.add_argument('-q', action='store_true', default=False, help='Quiet mode')
parser.add_argument('-v', action='store_true', default=False, help='Verbose mode')
parser.add_argument('commands', nargs='+', help='Sync delivieries')

try:
    args = parser.parse_args()
except:
    showhelp()
    raise SystemExit()

logging_startup(args)
#logging.basicConfig(format='%(message)s', level=log_level)

logging.info('Hello!')

for command in args.commands:
    execute(command, args)

