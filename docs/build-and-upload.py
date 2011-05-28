#!/usr/bin/env python

# To use this script, you must first checkout
# the devilry repository into ../../devilry-docwebsite
# (the same parentdir as this repo), and switch to the
# gh-pages branch:
#
#   cd ../../
#   git clone git@github.com:devilry/devilry-django.git devilry-docwebsite
#   git checkout --track origin/gh-pages
#
# After running this script, you must manually commit and push
# devilry.github.com.
from os.path import join, dirname, abspath, exists
from os import system, chdir
from shutil import rmtree, copytree
from sys import argv

if len(argv) != 2:
    raise SystemExit('usage: %s "<commitmsg>"' % argv[0])
commitmsg = argv[1]

this_dir = abspath(dirname(__file__))

version = 'dev'
repodir = join(dirname(dirname(this_dir)), 'devilry-docwebsite')
outdir = join(repodir, version)
indir = join(this_dir, '.build', 'html')


system("make clean html")

chdir(repodir)
system("git checkout gh-pages")
system("git reset --hard")
system("git clean -df")
if exists(outdir):
    rmtree(outdir)

copytree(indir, outdir)
system('git add .')
system('git commit -a -m "%s"' % commitmsg)
system('git push origin gh-pages')
