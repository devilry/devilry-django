from fabric.api import task, run, sudo
from fabric.contrib.files import exists
from fabric.context_managers import cd


repo = 'git://github.com/devilry/devilry-django.git'
branch = 'master'
checkout_dir = '/home/ubuntu/devilry-django'
prodenv_dir = checkout_dir + '/example-productionenv'


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
    with cd(prodenv_dir):
        run('fab refresh')


@task
def run_gunicorn_fg():
    with cd(prodenv_dir):
        run('bin/django_production.py run_gunicorn -w 4 127.0.0.1:9000')


@task
def run_nginx_fg():
    with cd(prodenv_dir):
        run('nginx -c {prodenv_dir}/server-conf/nginx.conf -g "daemon off;"'.format(prodenv_dir=prodenv_dir))


#####################
# Import awsfab tasks
#####################
from awsfabrictasks.ec2.tasks import *
from awsfabrictasks.regions import *
from awsfabrictasks.conf import *
