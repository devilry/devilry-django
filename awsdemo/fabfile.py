from fabric.api import task, run, sudo
from fabric.contrib.files import exists
from fabric.context_managers import cd


repo = 'git://github.com/devilry/devilry-django.git'
branch = 'master'
checkout_dir = '/home/ubuntu/devilry-django'
prodenv_dir = checkout_dir + '/example-productionenv'
gunicorn_pidfile = '/tmp/gunicorn.pid'


def _install(*packages):
    sudo('apt-get install --yes {0}'.format(' '.join(packages)))

@task
def install_requirements():
    """
    Install requirements for the demo.
    """
    _install('python-virtualenv', 'fabric', 'nginx', 'git', 'postgresql',
             'libpq-dev', 'python-dev', 'build-essential')

@task
def checkout_devilry():
    """
    Checkout or pull.
    """
    if not exists(checkout_dir):
        run('git clone {repo}'.format(repo=repo))
        with cd(checkout_dir):
            run('git checkout {branch}'.format(branch=branch))
    else:
        with cd(checkout_dir):
            run('git checkout {branch}'.format(branch=branch))
            run('git pull origin {branch}'.format(branch=branch))


@task
def refresh():
    """
    Refresh the virtualenv and rebuild static files.
    """
    with cd(prodenv_dir):
        run('fab refresh')

@task
def update_devilry():
    """
    Update devilry on aws.
    """
    stop_servers()
    with cd(prodenv_dir):
        run('fab update_devilry')
    start_servers()


@task
def setup():
    """
    Run install_requirements, checkout_devilry and refresh
    """
    install_requirements()
    checkout_devilry()
    refresh()


@task
def reset_demodb():
    with cd(prodenv_dir):
        run('fab reset_demodb')


@task
def start_servers():
    run('{prodenv_dir}/bin/django_production.py run_gunicorn -w 4 127.0.0.1:9000 --daemon --pid={pidfile}'.format(pidfile=gunicorn_pidfile,
                                                                                                                  prodenv_dir=prodenv_dir),
        pty=False)
    sudo('nginx -c {prodenv_dir}/server-conf/nginx.conf'.format(prodenv_dir=prodenv_dir), pty=False)


def _kill_by_pidfile(pidfile):
    if exists(pidfile):
        pid = run('cat {pidfile}'.format(pidfile=pidfile)).strip()
        sudo('kill {pid}'.format(pid=pid))
    else:
        print 'File does not exist:', pidfile

@task
def stop_servers():
    _kill_by_pidfile(gunicorn_pidfile)
    _kill_by_pidfile('/tmp/nginx.pid')


@task
def restart_servers():
    stop_servers()
    start_servers()


#####################
# Import awsfab tasks
#####################
from awsfabrictasks.ec2.tasks import *
from awsfabrictasks.regions import *
from awsfabrictasks.conf import *
