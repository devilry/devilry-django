#!/usr/bin/env python
# Clean the docs (removes docs/.build/)

from shutil import rmtree
from common import get_docs_build_dir
from os.path import exists


if exists(get_docs_build_dir()):
    rmtree(get_docs_build_dir())
