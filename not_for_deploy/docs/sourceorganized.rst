.. _sourceorganized:

========================================================
How the Devilry sources are organized
========================================================

The devilry source code lives in the ``src/`` directory. Each subdirectory is
a complete Python egg/package that we could have put on PyPI if we wanted.

We use the ``mr.developer`` buildout extension to handle this strucure. This means
that all the directories in ``src/`` has a corresponding declaration in
``eggs`` and and ``[sources]`` in ``buildout.cfg``, or one of the files it inherits from
(I.E.: ``buildout-base.cfg`` or ``development-base.cfg``).

There may be some non-local modules (external VCS repos) in ``src/`` if we are
fetching a dependency from VCS instead of the local filesystem.


#####################################
Why do we not use namespace packages?
#####################################

We do not use namespace packages because they work badly with Django. If we name an app
``devilry.admin``, its Django appname will be ``admin``. This is reflected in its database
tables, which will be named ``admin_XXXX``. Django has ways of avoiding this problem, but
none of them is as easy as simply using the ``devilry_``-prefix on all packages instead of
the ``devilry``-namespace.