# Vagrant setup for running the Devilry testsuite

## Why
Making selenium work is not easy. It is much easier to create a virtual machine
where the tests just work out of the box, with all the browsers installed.


## How

You should have a basic understanding of Vagrant before you start. Check out the getting started guide on http://vagrantup.com/.


### 1 - Install Vagrant and VirtualBox
See the getting started guide on http://vagrantup.com/.


### 2 - Create and boot a virtual machine with Vagrant

Run the following commands:

    $ cd /path/to/devilryrepo/vagrant
    $ vagrant up
    ... wait for vagrant to install everything
    ... (it gives you back the terminal when when it is finished)
    ... then we need to reload (basically restart)
    $ vagrant reload


## How to start, stop and reset

To 
