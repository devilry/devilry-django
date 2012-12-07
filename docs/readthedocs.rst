.. _readthedocs:

====================================================
How we make ReadTheDocs build our docs
====================================================


.. note::
    This is only useful if you need ot debug readthedocs errors, so it is
    intended for the devilry core developers.


The problem
###########
ReadTheDocs does not support buildout, but they support virtualenv and pip
requirement files. Since we use buildout, we do not maintain a pip requirements
file.


Solution
########
We use the ``buildout.dumprequirements`` buldout recipe to generate a pip
requirements file, store the generated file in the repo, and regenerate it when 
the docs break.



Building the docs in a virtualenv
###################################
::

    $ cd docs/
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt && pip install sphinx && make html

.. note::
    We intentionally do not use the same virtualenv as we use when
    generating/updating (below). This is to make sure the requirements-file
    work with a completely clean virtualenv.


Generating/updating requirements.txt
####################################

First generate ``requirements.txt``::

    $ cd docs/
    $ git clean -dfx . && virtualenv --no-site-packages venv2 && venv2/bin/easy_install zc.buildout && venv2/bin/buildout && venv2/bin/buildout

Then manually remove ``setuptools`` and ``distribute`` from
``requirements.txt``.

.. note:: Why we remove setuptools and distribute:

    They will be pulled in automatically thought other
    packages as needed, but specifying that they should be installed with a
    specific version just causes problems (pip cant install distribute, setuptools
    is already installed, ...). For example: https://bitbucket.org/tarek/distribute/issue/91/install-glitch-when-using-pip-virtualenv


.. note::
    Running ``bin/buildout`` twice is actually correct. The requirements file
    is almost empty adter the first run.
