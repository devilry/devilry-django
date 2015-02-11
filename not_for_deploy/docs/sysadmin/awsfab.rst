=====================================================
How to deploy a demo on AWS with awsfab and chef-solo
=====================================================



Get the sources
===============

Clone the sources for ``devilry-deploy``. You find them at our `GitHub project
page <https://github.com/devilry/devilry-deploy>`_


Install awsfab
==============

Install awsfab in a virtualenv in the awsfab-folder::

    $ cd awsfab/
    $ virtualenv --no-site-packages .
    $ bin/easy_install zc.buildout
    $ bin/buildout


Configure awsfab to use your AWS credentials
============================================

Create a keypair for the devilry demo
-------------------------------------
Go to http://console.aws.amazon.com, and select ``EC2 -> Key Pairs``. Create a
key named ``devilrydemo``. Put the ``.pem`` file in ``~/.ssh/``. Make sure you
set the permissions of your .pem-file so only you can access it:

    $ chmod 600 ~/.ssh/devilrydemo.pem

Configure your access key
-------------------------
Go to http://console.aws.amazon.com, and select ``Your name (in the header) -> Security credentials``.
Under the *Security credentials*-heading you will find your *Access Key ID*
and *Secret Access Key*. Create a file named ``awsfab_settings_local.py`` (in
the directory containing ``awsfab_settings.py``, and add the keys::

    AUTH = {'aws_access_key_id': 'Access Key ID',
            'aws_secret_access_key': 'Secret Access Key'}

    # If you want to put ``devilrydemo.pem`` another place than ~/.ssh/, set KEYPAIR_PATH
    #KEYPAIR_PATH = ['/path/to/dir/containing/key']

See http://awsfabrictasks.readthedocs.org/ for
more details.


Deploy with chef-solo and awsfab
================================

Launch/create a new EC2 instance for the webserver
--------------------------------------------------
Launch an EC2 ``m1.small`` instance with ubuntu-server::

    $ bin/awsfab ec2_launch_instance:devilrydemo0,ubuntu-SMALL

In this example, we name our instance ``devilrydemo0``, this means that the
``Name``-tag will be devilrydemo0. You can choose whatever name you like.


Install chef-solo on the instance
---------------------------------
Install chef-solo on the instance. You only need to do this once for each
instance. Make sure the name (after ``-E``), matches the one you picked for
``ec2_launch_instance`` above::

    $ bin/awsfab -E devilrydemo0 install_chefclient

Deploy the demo with chef-solo
------------------------------
With Chef, you always deploy a *node*. Each node is configured in a
``*.json``-file in ``REPOROOT/chef/nodes/``.

Deploy ``devilrydemo.json`` to ``devilrydemo0``::

    $ bin/awsfab -E devilrydemo0 chef_deploy:devilrydemo.json

Update
------
To update the demo, simply repeat the ``chef_deploy``-command.
