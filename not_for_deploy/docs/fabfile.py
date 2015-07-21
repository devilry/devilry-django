import os
import shutil
from fabric.api import local, task
import sys
import subprocess


@task
def docs():
    """
    Build the docs.
    """
    local('sphinx-build -b html . _build')

@task
def doc2dash():
    local('doc2dash -Af --name Devilry _build')

@task
def clean():
    """
    Remove all files built for the docs.
    """
    if os.path.exists('_build'):
        shutil.rmtree('_build')

def _open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        if sys.platform == "darwin":
            opener = "open"
        else:
            opener = "xdg-open"
        subprocess.call([opener, filename])

@task
def opendocs():
    """
    Open docs in the default browser.
    """
    _open_file('_build/index.html')
