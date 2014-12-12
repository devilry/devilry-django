#!/usr/bin/env python
# Build the docs as HTML using sphinx (using make html from docs/)

from common import get_docsdir, get_docs_buildhtml_dir, DevilryAdmArgumentParser
import os
from os.path import join
from subprocess import call
import webbrowser
from sys import exit


parser = DevilryAdmArgumentParser()
parser.add_argument('-b', '--openbrowser', action='store_true',
                    help='Open the docs in your default browser after building.')
parser.add_argument('--completionlist', action='store_true',
                   help='Print completionlist for bash completion.')
args = parser.parse_args()

if args.completionlist:
    print "--openbrowser"
    exit(0)

os.chdir(get_docsdir())
call(['make', 'html'])


indexpath = join(get_docs_buildhtml_dir(), 'index.html')

print '********************************************************************'
print 'HTML documentation for python code built successfully. View it here:'
print
print '   ', indexpath
print
print 'Use devilryadmin.py docs_upload_to_website to upload them to'
print 'the website if you have push permission on devilry/devilry-django/'
print '********************************************************************'

if args.openbrowser:
    print 'Opening in browser'
    webbrowser.open_new_tab('file:///' + indexpath)
