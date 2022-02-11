#######################################
How to setup error tracking with Sentry
#######################################

Sentry is an open-source error tracker service that either can 
be rented (SaaS) or `self-hosted <https://develop.sentry.dev/self-hosted/>`_.

********
Settings
********

The default way of setting up error tracking with Sentry is to 
use `Sentry's official Django integration <https://docs.sentry.io/platforms/python/guides/django/>`_.

Make sure Sentry's Python SDK is installed in Python environment::

    $ venv/bin/pip install --upgrade sentry-sdk

Then initialize the Django integration in the ``devilry_settings.py`` file::

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        integrations=[DjangoIntegration()],
    
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    
        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        # release="myapp@1.0.0",
    )

*****************
Settings (legacy)
*****************

Raven was the `official legacy Python client for Sentry <https://github.com/getsentry/raven-python>`_
that some legacy Sentry servers might still require.

Make sure Reven is installed in Python environment::

    $ venv/bin/pip install raven

Update ``devilry_settings.py`` file with Sentry project info and add mapping of Devilry versions::

    from devilry import __version__ as devilry_version
    
    (...)
    
    INSTALLED_APPS += ['raven.contrib.django.raven_compat']
    RAVEN_CONFIG = {
        'dsn': 'https:project_url@sentry.example.com',
        'release': devilry_version,
    }

***********
Whats next?
***********
After setting up Sentry you might also want to configure Devilry's logging:

- :doc:`logging`.
