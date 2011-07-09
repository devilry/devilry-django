#!/usr/bin/env python

import sys
from utils import execute, showhelp

if len(sys.argv) < 2:
    showhelp()
    raise SystemExit()

command = sys.argv[1]
execute(command)
#showhelp()
