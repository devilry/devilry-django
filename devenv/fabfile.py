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
def bootstrap(config='develop.cfg'):
    """
    Run bootstrap with the python executable in the virtualenv.
    """
    local('virtualenv/bin/python bootstrap.py -c {}'.format(config))


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
    Run ``bin/django_dev.py syncdb --noinput``
    """
    local('bin/django_dev.py syncdb --noinput')

@task
def reset():
    """
    Run the following tasks: clean, virtualenv, bootstrap, syncdb
    """
    clean()
    virtualenv()
    bootstrap()
    syncdb()
