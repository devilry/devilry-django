from os.path import exists
from os import remove
from fabric.api import local, abort, task



@task
def setup_demo():
    """
    Runs ``reset`` and ``autodb`` tasks.
    """
    reset()
    autodb()


@task
def remove_db():
    """ Remove ``db.sqlite3`` if it exists. """
    if exists('db.sqlite3'):
        remove('db.sqlite3')

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
          'untracked files in devenv/:')
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
    autogen_extjsmodels()

@task
def autodb():
    """
    Run ``remove_db``, ``syncdb`` and ``bin/django_dev.py dev_autodb -v2``
    """
    remove_db()
    syncdb()
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
    local('bin/django_dev.py runserver 0.0.0.0:8001 --settings settings.noextjsdebug')

@task
def jsbuild(appname):
    print
    print 'NOTE: Make sure:'
    print
    print '   bin/fab extjsbuild_server'
    print
    print 'is running in another terminal'
    local('bin/django_dev.py senchatoolsbuild --app {appname}'.format(appname=appname))

@task
def jsbuild_devilry_student():
    jsbuild('devilry_student')

@task
def jsbuild_devilry_frontpage():
    jsbuild('devilry_frontpage')

@task
def jsbuild_devilry_subjectadmin():
    jsbuild('devilry_subjectadmin')

@task
def jsbuild_all():
    jsbuild_devilry_student()
    jsbuild_devilry_frontpage()
    jsbuild_devilry_subjectadmin()
