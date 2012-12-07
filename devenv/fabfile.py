try:
    from devilry_developer.fabrictasks import *
except ImportError:
    print '*** WARNING: Could not import devilry_developer.fabrictasks. You should probably run "fab bootstrap" to create a virtualenv, then use ``bin/fab`` to execute Fabric tasks.'


from fabric.api import local, task

@task
def bootstrap():
    """
    Runs ``virtualenv --no-site-packages . && bin/easy_install zc.buildout && bin/buildout``.
    """
    local('virtualenv --no-site-packages .')
    local('bin/easy_install zc.buildout')
    local('bin/buildout')
