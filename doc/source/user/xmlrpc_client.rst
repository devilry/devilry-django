.. _user-xmlrpc_client:

================================================
Command line client
================================================



Install
#######################################################################


Quick install
-------------

You need the ``python-setuptools`` package to install the Devilry command line client. This package is installed on Mac OS X 10.5 and up.
On Ubuntu, run the following command to install it:

::

    sudo apt-get install python-setuptools

Then, run the following command to install the client:

::

    ~$ sudo easy_install -U devilry_xmlrpc_client

This command will generate several lines of output, among which you should locate the following line:

::

    Installing devilry-examiner.py script to /opt/local/Library/Frameworks/Python.framework/Versions/2.6/bin

Add the install path to you ``PATH`` environment variable. You can now run the client by running:

::

    ~$ devilry-examiner.py

Installation issues
-------------------

The command ``sudo easy_install devilry-xmlrpc-client`` might ask you to update your version of setuptools, by running:

::

    easy_install -U setuptools

If so, run this command first, the run ``easy_install devilry-xmlrpc-client`` again.

Getting started
#######################################################################

In order to use the Devilry command line client, you should have been given the following from your administrator:

**URL**: 
    The server url to connect to
**LOGIN-COMMAND**: 
    The login command to use. This will be either ``login`` or ``formlogin``. 

Start by creating a Devilry checkout directory and change to it. You may give this directory any name you want. 
In this guide, we use ``devilrycheckout``.

::

    ~$ mkdir devilrycheckout
    ~$ cd devilrycheckout

We then initalize with the server, using the **URL** given to you by your administrator:

::

    ~/devilrycheckout/$ devilry-examiner.py init URL

Login using:

::

    ~/devilrycheckout/$ devilry-examiner.py LOGIN-COMMAND

If your username in your current shell session is not the same as your username with the Devilry server, use the -u option:

::

    ~/devilrycheckout/$ devilry-examiner.py LOGIN-COMMAND -u username

The next step is to sync every delivery on every active assignment using:

::

    ~/devilrycheckout/$ devilry-examiner.py sync

To correct assignments and publish feedback, use the ``sync``, ``info``, ``feedback``, ``publish`` and ``unpublish`` commands. You can run the ``help`` command to get more info about each of these commands, for example:

:: 

    ~/devilrycheckout/$ devilry-examiner.py sync --help
    ~/devilrycheckout/$ devilry-examiner.py info --help

When you wish to update the local sync with new deliveries, or feedback
submitted by other examiners (if you work on assignments with more than one
examiner on each group), just run the ``login`` and ``sync`` commands within any directory
below the checkout-directory. You might not have to login more than about
once a day, but this varies depending on how the devilry-server is
configured.
