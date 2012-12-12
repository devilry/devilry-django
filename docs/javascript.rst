.. _javascript:

==================================================
JavaScript --- Libraries and guidelines/code style
==================================================

Most of our UIs are developed in JavaScript using the ExtJS4 framework from Secha (http://sencha.com).


Libraries
#########
At the time of writing, we only use ExtJS4. We are open to including more libraries, but we have not
had the need yet.


Guidelines and code style
##########################

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



.. _jshint:

JSHint
######

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