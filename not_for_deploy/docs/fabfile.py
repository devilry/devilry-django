import os
import shutil
from fabric.api import local, task


@task
def docs():
    """
    Build the docs.
    """
    local('sphinx-build -b html . _build')


@task
def clean():
    """
    Remove all files built for the docs.
    """
    if os.path.exists('_build'):
        shutil.rmtree('_build')
