from os.path import exists, join, relpath
from os import remove, getcwd
# from shutil import rmtree, make_archive
# from zipfile import ZipFile
from fabric.api import local, abort, task
from fabric.context_managers import shell_env, lcd


DB_FILE = join('developfiles', 'db.sqlite3')
LANGUAGES = ['en', 'nb']


def _managepy(args, djangoenv='develop', environment={}, working_directory=None):
    working_directory = working_directory or getcwd()
    managepy_path = relpath('manage.py', working_directory)
    with shell_env(DJANGOENV=djangoenv, **environment):
        with lcd(working_directory):
            local('python {managepy_path} {args}'.format(managepy_path=managepy_path, args=args))


@task
def remove_db(djangoenv='develop'):
    """ Remove ``db.sqlite3`` if it exists. """
    if djangoenv == 'develop':
        if exists(DB_FILE):
            remove(DB_FILE)
    else:
        _managepy('dbdev_destroy', djangoenv=djangoenv)



@task
def syncmigrate(djangoenv='develop'):
    """
    Run ``bin/django_dev.py syncmigrate -v0 --noinput``
    """
    _managepy('syncdb -v0 --noinput', djangoenv=djangoenv)
    _managepy('migrate -v0 --noinput', djangoenv=djangoenv)

@task
def reset_db(djangoenv='develop'):
    """ Run ``remove_db`` followed by ``syncmigrate``. """
    remove_db(djangoenv=djangoenv)
    if djangoenv != 'develop':
        _managepy('dbdev_init', djangoenv=djangoenv)
    syncmigrate(djangoenv=djangoenv)


# @task
# def sandbox():
#     _managepy('devilry_sandboxcreate -s "duck2050" -l "DUCK2050 - Programmering uten grenser"')


@task
def autodb(djangoenv='develop', no_groups=False):
    """
    Run ``remove_db``, ``syncmigrate`` and ``bin/django_dev.py devilry_developer_old_autodb -v2``

    :param djangoenv: The DJANGOENV to use.
    :param no_groups: Use ``autodb:no_groups=yes`` to run devilry_developer_old_autodb with --no-groups.
    """
    no_groups = no_groups == 'yes'
    autodb_args = ''
    if no_groups:
        autodb_args = '--no-groups'
    reset_db(djangoenv=djangoenv)
    _managepy('devilry_developer_old_autodb -v2 {}'.format(autodb_args))
    # _managepy('rebuild_index --noinput')


@task
def demodb(djangoenv='develop'):
    """
    Run ``remove_db``, ``syncmigrate`` and ``bin/django_dev.py devilry.project.develop_demodb``

    :param djangoenv: The DJANGOENV to use.
    """
    reset_db(djangoenv=djangoenv)
    _managepy('devilry_developer_demodb',
        djangoenv=djangoenv,
        environment={
            'DEVILRY_EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend'
        })


def _demodb_managepy(command, djangoenv):
    _managepy(command,
        djangoenv=djangoenv,
        environment={
            'DEVILRY_EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend'
        })


@task
def new_demodb(djangoenv='develop'):
    """
    Run ``remove_db``, ``syncmigrate`` and ... TODO

    :param djangoenv: The DJANGOENV to use.
    """
    reset_db(djangoenv=djangoenv)
    _demodb_managepy('devilry_developer_demodb_createusers', djangoenv=djangoenv)
    # _demodb_managepy('devilry_developer_demodb_createnode duckburgh', djangoenv=djangoenv)
    # _demodb_managepy('devilry_developer_demodb_createsubject --node=duckburgh duck1010', djangoenv=djangoenv)
    # _demodb_managepy(
    #     'devilry_developer_demodb_createperiod --subject=duck1010 '
    #     '--starts-in-months -4 --duration-months 6 spring2015',
    #     djangoenv=djangoenv)
    # _demodb_managepy(
    #     'devilry_developer_demodb_create_pointassignment --period=duck1010.spring2015 '
    #     '--publishing-time-in-days -14 week1',
    #     djangoenv=djangoenv)
    # _demodb_managepy(
    #     'devilry_developer_demodb_create_pointassignment --period=duck1010.spring2015 '
    #     '--publishing-time-in-days 10 week2',
    #     djangoenv=djangoenv)



# def _gzip_file(infile):
#     import gzip
#     f_in = open(infile, 'rb')
#     gzipped_outfile = '{0}.gz'.format(infile)
#     f_out = gzip.open(gzipped_outfile, 'wb')
#     f_out.writelines(f_in)
#     f_out.close()
#     f_in.close()
#     remove(infile)


# def _get_stashdir(home):
#     from os.path import expanduser
#     from os import getcwd
#     if home == 'yes':
#         return join(expanduser('~'), '.devilry_db_and_deliveries_stash')
#     else:
#         return join(getcwd(), 'db_and_deliveries_stash')

# @task
# def stash_db_and_deliveries(home=False):
#     """
#     Dump the database and deliveries into the
#     ``db_and_deliveries_stash/``-directory.

#     :param home:
#         Use ``home=yes`` to stash to ``~/.devilry_db_and_deliveries_stash``
#         instead of ``<this dir>/db_and_deliveries_stash/``
#     """
#     stashdir = _get_stashdir(home)
#     if exists(stashdir):
#         rmtree(stashdir)
#     mkdir(stashdir)

#     # DB
#     dbdumpfile = join(stashdir, 'dbdump.sql')
#     backup_db(dbdumpfile)
#     _gzip_file(dbdumpfile)

#     # Delivery files
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     log = logging.getLogger('files.zip')
#     make_archive(join(stashdir, 'files'), 'zip', logger=log, base_dir="deliverystorehier")


# def _gunzip_file(gzipped_infile):
#     import gzip
#     unzipped = gzip.open(gzipped_infile, 'rb').read()
#     outfile = gzipped_infile.replace('.gz', '')
#     open(outfile, 'wb').write(unzipped)
#     return outfile



# @task
# def unstash_db_and_deliveries(home=False):
#     """
#     Undo ``stash_db_and_deliveries``.

#     :param home:
#         Use ``home=yes`` to unstash from ``~/.devilry_db_and_deliveries_stash``
#         instead of ``<this dir>/db_and_deliveries_stash/``
#     """
#     # DB
#     stashdir = _get_stashdir(home)
#     dbfile = _gunzip_file(join(stashdir, 'dbdump.sql.gz'))
#     restore_db(dbfile)
#     remove(dbfile) # We remove the unzipped dbdump, but keep the .gz

#     # Delivery files
#     if exists('deliverystorehier'):
#         rmtree('deliverystorehier')
#     zipfile = ZipFile(join(stashdir, 'files.zip'))
#     zipfile.extractall()


# @task
# def backup_db(sqldumpfile):
#     """
#     Dumps a backup of ``db.sqlite3`` to the given ``sqldumpfile``.

#     :param sqldumpfile: The SQL file to write the dump to.
#     """
#     local('sqlite3 db.sqlite3 .dump > {sqldumpfile}'.format(**vars()))

# @task
# def restore_db(sqldumpfile):
#     """
#     Restore ``db.sqlite3`` from the given ``sqldumpfile``.

#     :param sqldumpfile: The SQL file to restore the database from.
#     """
#     from os.path import exists
#     if exists(DB_FILE):
#         remove(DB_FILE)
#     local('sqlite3 db.sqlite3 < {sqldumpfile}'.format(**vars()))


@task
def jsbuild(appname, nocompress=False, watch=False, no_jsbcreate=False, no_buildserver=False):
    """
    Use ``bin/django_dev.py senchatoolsbuild`` to build the app with the given
    ``appname``.

    :param appname: Name of an app (E.g.: devilry.devilry_frontpage).
    :param nocompress: Run with ``--nocompress``. Good for debugging.
    :param watch: Run with ``--watch ../src/``. Good for development.
    :param no_jsbcreate:
        Do not re-create app.jsb3 (the slowest part of building)?
        Re-creating the jsb-file is only needed when you add requirements/deps
        or new files. Set to ``true`` to not generate JSB-file, or set to
        ``next`` and use --watch to generate the jsb-file at startup, but
        not when the watcher triggers re-build.
    :param no_buildserver:
        Do not run the buildserver.

    Workaround if the buildserver hangs (gets lots of 500 responses):

        $ DJANGOENV=extjsbuild python manage.py runserver 127.0.0.1:15041
        ... and in another shell:
        $ fab jsbuild:devilry.devilry_subjectadmin,no_buildserver=true
    """
    extra_args = []
    if no_buildserver:
        extra_args.append('--dont-use-buildserver')
    if nocompress:
        extra_args.append('--nocompress')
    if watch:
        extra_args.append('--watch ../src/')
    if no_jsbcreate:
        if no_jsbcreate == 'next':
            if not watch:
                abort('no_jsbcreate="next" only makes sense with --watch')
            jsbuild(appname, nocompress, watch=False) # build one with no_jsbcreate=False
        extra_args.append('--no-jsbcreate')
    extra_args = ' '.join(extra_args)
    _managepy(
        'senchatoolsbuild {extra_args} --app {appname}'.format(appname=appname, extra_args=extra_args),
        djangoenv='extjsbuild')


@task
def makemessages():
    for languagecode in LANGUAGES:
        _managepy(
            'makemessages '
            '--ignore "static*" '
            '-l {}'.format(languagecode), working_directory='devilry')


@task
def makemessages_javascript():
    """
    Build
    """
    for languagecode in LANGUAGES:
        _managepy(
            'makemessages '
            '-d djangojs '
            '--ignore "app-all.js" '
            '--ignore "all-classes.js" '
            '--ignore "node_modules" '
            '--ignore "bower_components" '
            '-l {}'.format(languagecode), working_directory='devilry')

@task
def compilemessages():
    _managepy('compilemessages', working_directory='devilry')
