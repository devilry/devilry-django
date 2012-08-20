# Devilry development environment

See ../README.md for info about setting it up.


## Building the ExtJS javascript apps

Run the buildserver (a Django server with a config that does not require login):

    $ fab extjsbuild_server

In another shell, while the server is running, use one of the build tasks:

    $ fab jsbuild_all
    or
    $ fab jsbuild_devilry_subjectadmin
    ... use:
    $ fab -l
    to list all tasks
