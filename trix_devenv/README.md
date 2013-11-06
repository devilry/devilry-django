Development setup for the Trix system on top of Devilry. Follow the
instructions for setting up a Devilry development environment (see
http://devilry.readthedocs.org), but use ``trix_devenv/`` instead of
``devenv/``.


## Add Trix to settings

After setting up a development environment, you will have to patch the
Devilry/Django settings to develop Trix.

### INSTALLED_APPS
Update ``src/devilry_settings/devilry_settings/default_settings.py`` with the
following at the end of ``INSTALLED_APPS``:

    'trix',
    'trix_extjshelpers',
    'trix_restful',
    'trix_simplified'

### URLs
Update ``src/devilry_settings/devilry_settings/default_settings.py`` with:

    (r'^trix/', include('trix.urls')),


### Notes about improving this setup
We should create a set of custom settings-files and a ``default_trix_urls.py``
in the ``trix``-package, and couple that with overrides for all the
``django_*``-sections from ``development-base.cfg`` in
``trix_devenv/buildout.cfg`` That way, none of the paching above would be
required. For now, we have simply left the stuff above commented out.


## Tips
Use ``bin/fab autodb:no_groups=yes`` instead of ``bin/fab autodb`` to generate
a bit less data. Devilry groups is not used by Trix, so you do not need them.
