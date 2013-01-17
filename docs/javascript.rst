.. _javascript:

==================================================
JavaScript --- Libraries and guidelines/code style
==================================================

Most of our UIs are developed in JavaScript using the ExtJS4 framework from Secha (http://sencha.com).

#################################################
Libraries
#################################################
At the time of writing, we only use ExtJS4. We are open to including more libraries, but we have not
had the need yet.


##################################################
Guidelines and code style
##################################################

Indent
    4 spaces
Naming
    Real meaningful names like::

        var age = 10;
        var username_to_name_map = {peterpan: 'Peter', wendy: 'Wendy'};

    NOT::

        var a = 10;
        var u = {peterpan: 'Peter', wendy: 'Wendy'};
        var usrmap = {peterpan: 'Peter', wendy: 'Wendy'};

Private methods and functions
    Same format as semi-private python methods/functions (prefix by ``_``)::

        _my_private_method: function() {
            return null;
        }

Code format
    Should pass without any errors from JSHint (see :ref:`jshint`).
Code layout
    The ExtJS app layout. See the ``devilry_subjectadmin`` app and the ExtJS4 docs.
Documentation
    Use the JSDuck format (https://github.com/senchalabs/jsduck). Note that you do not have to
    document every single function, but you should at least document:

    - Functions, methods and variables used outside its context (I.E.: you do not have to
      document view-functions that is only used by its controller, but you have to document it
      of multiple controllers use it).
    - Properties and config parameters for ExtJS classes.
    - Events for ExtJS classes, especially if they are used outside their controller.
File naming
    Name controllers by what the control (E.g: ``controller/period/PeriodController.js``), and the
    views after their purpose (E.g.: ``view/period/PeriodOverview.js``). Try to use unique names
    instead of generic names like ``Overview.js``. To see why, try to find (quick open) a file with
    tens of matches in an IDE like PyCharm or Eclipse that only search for file names, not for
    folder names (hint: it is not quick to open such files). We learned this when developing
    ``devilry_subjectadmin`` with controllers and views named ``Overview.js``.



.. _jshint:

####################################################
JSHint
####################################################

For info about JSHint, see http://www.jshint.com/.


Install
=======

Install NodeJS and Node Package Manager (part of NodeJS):

- Ubuntu: ``sudo apt-get install nodejs npm``
- OSX with homebrew: ``brew install npm``
- Others, see: http://nodejs.org/

Install JSHint in ``/usr/local`` on most nix systems, like Linux and OSX::

    $ sudo npm install jshint -g



Usage
=====
Simply point JSHint at a directory::

    $ jshint src/devilry_subjectadmin/devilry_subjectadmin/static/devilry_subjectadmin/app/

The defaults are sane (unlike JSLint), so you should not need to supply any options.

You can also use JSHint with :ref:`pycharm`.





############################################
Building the ExtJS javascript apps
############################################

.. note::
    This is only needed if you have made changes to javascript sources, or if you are making
    your own ExtJS app.


Dependencies
===================================

You need to install `Sencha tools
2 <http://www.sencha.com/products/sdk-tools/download/>`_ to build the
ExtJS javascript apps. Sencha tools requires an Oracle Java Runtime Environment.


The tasks
===================================

Use one of the jsbuild task. Use ``bin/fab -d jsbuild`` for docs. Example::

    $ cd devenv/
    $ bin/fab jsbuild:devilry_subjectadmin

To build without compressing the JS-sources (**for debugging**)::

    $ cd devenv/
    $ bin/fab jsbuild:devilry_subjectadmin,nocompress=true


Watch the filesystem for changes and rebuild
--------------------------------------------

Call the tasks with ``watch=true``. E.g.::

    $ cd devenv/
    $ bin/fab jsbuild:devilry_subjectadmin,nocompress=true,watch=true

You probably want to use::

    $ cd devenv/
    $ bin/fab jsbuild:devilry_subjectadmin,nocompress=true,watch=true,no_jsbcreate=next

to create a JSB-file on startup, but no on each watcher-trigger. This
speeds up rebuild significantly, but you will have to re-start
``jsbuild`` when you add requires or new files.


Broken pipe errors
===================================

You will most likely get a lot of broken pipe errors. This does not seem
to cause any problems with the build.