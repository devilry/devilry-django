# Devilry development environment

See ../README.md for info about setting it up.


## Building the ExtJS javascript apps
(only needed if you have made changes to their javascript sources)

Use one of the jsbuild_* tasks. Use ``fab -l`` to list them all. Example:

    $ fab jsbuild_devilry_subjectadmin

To build without compressing the JS-sources (**for debugging**):

    $ fab jsbuild_devilry_subjectadmin:nocompress=true

## Watch the filesystem for changes and rebuild

Just call the tasks with ``watch=true``. E.g.:

    $ fab jsbuild_devilry_subjectadmin:nocompress=true,watch=true


### Broken pipe errors
You will most likely get a lot of broken pipe errors. This does not seem to cause any problems with the build.
