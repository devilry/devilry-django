from os import remove, rename, listdir, getcwd, chdir
from fabric.api import local, abort, task
from os.path import join, exists, dirname, abspath


@task
def virtualenv():
    """
    Setup a virtualenv in virtualenv/.
    """
    local('virtualenv virtualenv')

@task
def bootstrap():
    """
    Run bootstrap with the python executable in the virtualenv.
    """
    local('virtualenv/bin/python ../bootstrap.py')

@task
def buildout():
    """
    Run bin/buildout.
    """
    local('bin/buildout')

@task
def clean():
    """
    Run ``git clean -dfx``. Asks for confirmation before running.
    """
    print('Are you sure you want to completely reset the environment? This '
          'will run "git clean -dfx --exclude src/", which removes any '
          'untracked files except those in src/, i.e:')
    local('git clean -ndfx .')
    ok = raw_input('Proceed (y/N)? ')
    if ok != 'y':
        abort('Aborted')
    local('git clean -dfx .')

@task
def syncdb():
    """
    Run ``bin/django_dev.py syncdb -v0 --noinput``
    """
    local('bin/django_dev.py syncdb -v0 --noinput')

@task
def autogen_extjsmodels():
    """
    Run ``bin/django_dev.py dev_autogen_extjsmodels``
    """
    local('bin/django_dev.py dev_autogen_extjsmodels')

@task
def reset():
    """
    Run the following tasks: clean, virtualenv, bootstrap, buildout, syncdb
    """
    clean()
    virtualenv()
    bootstrap()
    buildout()
    syncdb()
    autogen_extjsmodels()

@task
def autodb():
    """
    Run ``bin/django_dev.py dev_autodb -v2``
    """
    local('bin/django_dev.py dev_autodb -v2')

@task
def extjsbuild_server():
    """
    Run ``bin/django_dev.py runserver --settings settings.extjsbuild``
    """
    local('bin/django_dev.py runserver --settings settings.extjsbuild')


@task
def noextjsdebug_server():
    """
    Run ``bin/django_dev.py runserver --settings settings.noextjsdebug``
    """
    local('bin/django_dev.py runserver --settings settings.noextjsdebug')
