.. _buildout:

================================================================================
Buildout
================================================================================


#####################
Basics
#####################

.. _buildout_basics:

When do I have to re-run bin/buildout?
======================================
Whenever your or someone else makes changes to the buildout configuration files.



.. _understanding_buildout:

##########################
Understanding buildout
##########################

Website: http://www.buildout.org/

The essence of understanding buildout is in understanding how simple it is. Buildout:

1. reads your config file (the one you supply with ``-c``, or ``buildout.cfg``
   if none is supplied).
2. Looks for the ``parts`` attribute in the ``[buildout]`` section.
3. Split ``parts`` by whitespace and for each part:

   - Look up ``[<part>]``
   - Check that it has a ``recipie``-attribute.
   - Run the recipe (download and install it if it is not installed).

This is essentially all that buildout does. Note that buildout configs can
extend other configs as explained in :ref:`configuring_buildout`.


The [pythonwrapper] section in buildout-base.cfg
================================================
This section generates ``bin/pythonwrapper`` which is a wrapper for the python
executable used to run ``bootstrap.py``. The wrapper simply resets ``sys.path``
to only include the python modules listed in the ``eggs`` attribute.
Open ``bin/pythonwrapper`` in an editor and see how it is implemented.


The [django_<something>] sections
=================================
Just like the ``python`` sections, however their recipe generates wrappers for
the django management commands (just like ``manage.py``).


More help?
==========
See the comments in ``buildout-base.cfg`` and ``development-base.cfg``.



.. _configuring_buildout:

################################################################
Configuring buildout
################################################################

Buildout is configured in ``buildout-base.cfg``, ``development-base.cfg``,
``devenv/buildout.cfg`` and ``prodenv_*/buildout.cfg``. The
configuration in ``devenv/`` and ``prodenv_*/`` are completely separate
buildout environments, except that they both extend ``buildout-base.cfg``.
This means that the files generated in ``devenv/`` does not affect ``prodenv_*/``,
and it means that you can experiment with changes in ``devenv/buildout.cfg``
without affecting the production deployment settings.


.. _buildoutattributes:

####################################################
Buildout attributes
####################################################

Override attributes
===================
A typical use-case for overriding attributes are development versions of
dependencies::

    [versions]
    Django = 5.0-beta2

Extend attributes
=================
You can extend attibutes with ``+=``. One use-case is adding another part::

    [buildout]
    parts +=
        sphinxbuilder


Reference attributes
====================
Attributes can be referenced anywhere in the buildout config. The format is
${<section>:<attribute>}. A couple of useful builtin attributes:

  ${buildout:directory} ==> <this dir (devenv/ if buildout.cfg is in devenv/>
  ${buildout:bin-directory} ==> ${buildout:directory}/bin



Configfile inheritance
======================
When you extend a buildout config, all its attributes are inherited, and you can replace and extend
attributes. You extend a buildout config using the ``buildout:extends``-attribute::

    [buildout]
    extends = ../development-base.cfg



Add dependencies
================
Add eggs to the ``eggs``-attribute in ``buildout-base.cfg``, or extend the ``eggs``-attribute in
any config extending ``buildout-base.cfg`` (see :ref:`buildoutattributes`)


Specify versions
================

In ``versions.cfg``. When you add new dependencies, you can just run
``bin/buildout``, and see what new packages and versions the new dependency
installs.


Check for new versions
----------------------

Run::

    $ bin/checkversions -v -l 1 ../versions.cfg

See: http://pypi.python.org/pypi/z3c.checkversions/ for more details.


Buildout cache
==============
``buildout.cfg`` is is configured to use the
``/path/to/reporoot/buildoutcache/`` as cache for downloaded and
compiled eggs. This speeds up buildout without having to configure a global
buildout cache.


When buildout is down
=====================

When you get the following from buildout::

    Download error: [Errno 60] Operation timed out

or::

    Download error: [Errno 110] Connection timed out

it usually means that the primary buildout mirror is down. To set an
alternative mirror, just uncomment one of the ``index`` attributes in the
``[buildout]`` section of ``buildout-base.cfg`` to use a mirror.


###########################################
Omelette --- browse sources of dependencies
###########################################

If you find that you need to browse the sources of our dependencies, the
``collective.recipe.omelette`` is great.  It synmlinks all our
sources in a flat hierarchy in ``devenv/parts/omelette/`` (including flattening
namespace packages). This means that we can:

    - Browse the sources of all our dependencies in one place (and use grep for
      searching).
    - Modify these sources and insert debugging statements.



##############################################################################
Advantages of buildout
##############################################################################
- Easy to get started on a new machine. Only a working Python is required. Manages your PYTHONPATH through wrappers in ``bin/``.
- You can reset ``devenv`` at any time using ``git clean -dfx devenv/``, and re-run bootstrap and buildout to get a clean development environment.
- You can copy ``devenv`` to set up multiple configurations of devilry with different settings. An example of this is ``example-productionenv/``.
