# AWS demo creator

This directory contains everything needed to easily setup a Devilry demo on an
Amazon Web Services EC2 micro instance.

## Required steps

### Get the required python packages
You only need to do this once (or when the dependencies have updates):

    $ virtualenv virtualenv
    $ virtualenv/bin/python ../bootstrap.py
    $ bin/buildout


### Create a keypair for the devilry demo
Go to http://console.aws.amazon.com, and select ``EC2 -> Key Pairs``. Create a
key named ``devilrydemo``. Put the ``.pem`` file in ``~/.ssh/``. Make sure you
set the permissions of your .pem-file so only you can access it:

    $ chmod 600 ~/.ssh/devilrydemo.pem


### Create awsfab_settings_local.py
Every setting except your authentication token is already configured in ``awsfab_settings.py``. You only need to
copy ``awsfab_settings_local-skel.py`` to ``awsfab_settings_local.py``, and
edit the ``AUTH`` variable in ``awsfab_settings_local.py``.

### Make sure it works
Run:

    $ bin/awsfab list_regions

If this lists AWS regions without any errors, you should be good to go.

### Create an AWS instance
Run:

    $ bin/awsfab ec2_launch_instance:devilrydemo1,default

to create a AWS instance using named ``devilrydemo1`` using the ``default``
settings in ``awsfab_settings.EC2_LAUNCH_CONFIGS``. This creates a AWS
micro instance, which is the cheapest AWS instance.

### Setup your AWS instance to run Devilry
Run:

    $ bin/awsfab -E devilrydemo1 setup


### Create the demodb

    $ bin/awsfab -E devilrydemo1 reset_demodb


### Run the demo (you can do this while the demodb is beeing created)

    $ bin/awsfab -E devilrydemo1 start_servers

Use ``stop_servers`` and ``restart_servers`` to stop/restart the servers.



## Update the demo

    $ bin/awsfab -E devilrydemo1 update_devilry


## Tip - Store settings and keys in the cloud
If you have a cloud drive, like Google Drive or Dropbox, you may want to put
your ``devilrydemo.pem`` and ``awsfab_settings_local.py`` on your cloud drive.
This has some security problems, however it should not be a huge issue as long
as you do not use your AWS account for anything but demos/testing.

``awsfab_settings_local-skel.py`` has a commented out ``KEYPAIR_PATH`` that you
can copy into your ``awsfab_settings_local.py``. Just make sure you do not have
any whitespace in the path.

``awsfab_settings_local.py`` can be symlinked from your cloud storage provider
directory. Note that you may not want to do this, since
awsfab_settings_local.py contains your AWS security credentials.
