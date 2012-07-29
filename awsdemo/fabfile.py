from fabric.api import task, run, sudo



@task
def install_requirements():
    """
    Run ``uname -a``
    """
    sudo('uname -a')



#####################
# Import awsfab tasks
#####################
from awsfabrictasks.ec2.tasks import *
from awsfabrictasks.regions import *
from awsfabrictasks.conf import *
