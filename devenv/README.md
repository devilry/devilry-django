# Devilry development environment

See ../README.md for info about setting it up.


## Building the ExtJS javascript apps
(only needed if you have made changes to their javascript sources)


### Dependencies

You need to install [Sencha tools 2](http://www.sencha.com/products/sdk-tools/download/) to build the ExtJS javascript apps.

NOTE: Sencha tools requires a Oracle Java Runtime Environment.


### The tasks

Use one of the jsbuild task. Use ``fab -d jsbuild`` for docs. Example:

    $ fab jsbuild:devilry_subjectadmin

To build without compressing the JS-sources (**for debugging**):

    $ fab jsbuild:devilry_subjectadmin,nocompress=true


## Watch the filesystem for changes and rebuild

Install watchdog:

    $ virtualenv/bin/easy_install watchdog

Call the tasks with ``watch=true``. E.g.:

    $ fab jsbuild:devilry_subjectadmin,nocompress=true,watch=true

You probably want to use:

    $ fab jsbuild:devilry_subjectadmin,nocompress=true,watch=true,no_jsbcreate=next

to create a JSB-file on startup, but no on each watcher-trigger. This speeds up
rebuild significantly, but you will have to re-start ``jsbuild`` when you add requires or new files.
    



### Broken pipe errors
You will most likely get a lot of broken pipe errors. This does not seem to cause any problems with the build.
