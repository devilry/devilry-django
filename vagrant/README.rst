===============================================
Vagrant setup for running the Devilry testsuite
===============================================

Why
###
Making selenium work is not easy. It is much easier to create a virtual machine
where the tests just work out of the box, with all the browsers installed.


How
###

You should have a basic understanding of Vagrant before you start. Check out
the getting started guide on http://vagrantup.com/.


1 - Install Vagrant and VirtualBox
==================================
See the getting started guide on http://vagrantup.com/.


2 - Create and boot a virtual machine with Vagrant
==================================================

Run the following commands:

    $ cd /path/to/devilryrepo/vagrant
    $ vagrant up
    ... wait for vagrant to install everything
    ... (it gives you back the terminal when when it is finished)
    ... then we need to reload (basically restart)
    $ vagrant reload


3 - Copy devenv/ and run bootstrap buildout
===========================================

We need to use a separate virtualenv and set of packages for our Vagrant
Virtual Machine. The easiest way to achive this is to copy ``devenv``::

    $ cd /path/to/devilryrepo/vagrant
    $ vagrant ssh
    $ cd /reporoot
    $ mkdir vagrant_devenv/
    $ cp devenv/buildout.cfg devenv/fabfile.py vagrant_devenv/
    $ cd vagrant_devenv/
    $ fab bootstrap

.. note::
    ``devenv_vagrant/`` is in ``.gitignore``, so you do not have to be afraid
    to add it to the repo by accident.


4 - Run tests
=============

Ssh to the vagrant machine (if you are not already there)::

    $ cd /path/to/devilryrepo/vagrant
    $ vagrant ssh

Go to the``vagrant_devenv``-dir that we created in *step 3*, and run tests. E.g::

    $ cd /reporoot/vagrant_devenv
    $ DISPLAY=:0.0 bin/django_test.py test devilry_subjectadmin


.. note::
    We use ``DISPLAY=:0.0`` to open the tests-browsers in the virtual machine,
    while we use SSH. You can, alternatively, work in the desktop-environment in
    the virtual machine, using ``xterm`` to run the tests.

    Normally, ``ssh`` provides a better development experience, because it is
    easier to browse, copy, paste, etc.., from an ssh-shell in your preferred
    terminal.


Issues
######
- Chrome does not work in the virtual machine.


About the setup
###############

- We mount the root of our repo at ``/reporoot``.
- We mount using NFS because the SAMBA with symlink emulation is too slow (at
  least 20 times slower). This is not because Samba is slow, but because the
  symlink emulation layer uses copies to emulate symlinks.
