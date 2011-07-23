#!/usr/bin/env python
# Upload the current docs/.build/html/ to the dev/ directory of the gh-pages branch of devilry/devilry-django. Depends on "docs" and "jsdocs -c -b".


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

from os import system, chdir, getcwd
from os.path import join
from shutil import rmtree, copytree
from tempfile import mkdtemp

from common import get_docs_buildhtml_dir, depends, Command

depends(Command('docs'),
        Command('docs_js'))


repo_rw_url = 'git@github.com:devilry/devilry-django.git'
version = 'dev'
indir = get_docs_buildhtml_dir()

try:
    tempdir = mkdtemp()
    print 'Created temp dir', tempdir

    print 'Checking out devilry repo to tempdir.'
    chdir(tempdir)
    system("git clone --branch gh-pages {0} devilry".format(repo_rw_url))

    repocheckoutdir = join(tempdir, 'devilry')
    chdir(repocheckoutdir)
    system("git reset --hard")
    system("git clean -df")
    system("ls")
    system("pwd")

    outdir = join(repocheckoutdir, version)
    print outdir
    rmtree(outdir) # Remove everything (git autodetects files that we delete and add again as modified)
    copytree(indir, outdir)
    system('git add .')
    system('git status')
    system('git commit -a -m "updated docs"')
    system('git push origin gh-pages')
finally:
    try:
        rmtree(tempdir)
    except:
        pass
