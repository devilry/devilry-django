Development setup for the Trix system on top of Devilry.

Follow the instructions for setting up a Devilry development environment (see
http://devilry.readthedocs.org), but use ``trix_devenv/`` instead of
``devenv/``.

## Add Trix to settings

After setting up a development environment, you will have to patch the
Devilry/Django settings to develop Trix.

### INSTALLED_APPS
Update ``src/devilry_developer/devilry_developer/settings/base.py`` with the
following at the end of ``INSTALLED_APPS``:

    'trix',
    'trix_extjshelpers',
    'trix_restful',
    'trix_simplified'

### URLs
Update ``src/devilry_developer/devilry_developer/dev_urls.py`` with the following
url:

    (r'^trix/', include('trix.urls')),


### Notes about improving this setup
We should create a set of custom settings-files and a ``default_trix_urls.py``
in the ``trix``-package, and couple that with overrides for all the
``django_*``-sections from ``development-base.cfg`` in
``trix_devenv/buildout.cfg`` That way, none of the patching above would be
required. For now, we have simply left the stuff above commented out.


## Tips

- Use ``bin/fab autodb:no_groups=yes`` instead of ``bin/fab autodb`` to generate
  a bit less data. Devilry groups is not used by Trix, so you do not need them.
- `devilry-deploy <http://devilry-deploy.readthedocs.org/>`_ has a Vagrant
  setup for testing Trix in a VM.


## The package trix_SOMETHING is dirty?
You may get some warnings like this when you re-run ``fab bootstrap``:

    The package 'trix_extjshelpers' is dirty.
    Do you want to update it anyway? [yes/No/all]

That is because the repos are not clean (``git status`` on them reports changed or untracked files).


## Editing in the Trix repos fetched by buildout?
This is perfectly safe. As you can see from the section about dirty packages
above, buildout even warns when you are in danger of overwriting local changes.
We also setup a custom default push url to an url that works when you have
push-permissions to the repos. If you are working on a fork, you may want to
modify the pushurl in ``trix_devenv/buildout.cfg`` and re-run fab bootstrap.
