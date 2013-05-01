try:
    from devilry_developer.fabrictasks import *
except ImportError:
    print '*** WARNING: Could not import devilry_developer.fabrictasks. You should probably run "fab bootstrap" to create a virtualenv, then use ``bin/fab`` to execute Fabric tasks.'


from fabric.api import local, task

@task
def bootstrap():
    """
    Runs ``virtualenv --no-site-packages venv && venv/bin/python ../bootstrap.py && bin/buildout && bin/fab postbootstrap``.
    """
    local('virtualenv --no-site-packages venv')
    local('venv/bin/python ../bootstrap.py')
    local('bin/buildout')
    local('bin/fab postbootstrap')
