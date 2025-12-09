###########################################
How to configure error tracking with Sentry
###########################################

Sentry is an open-source error tracker service that either can 
be rented (SaaS) or `self-hosted <https://develop.sentry.dev/self-hosted/>`_.

********
Settings
********

The default way of setting up error tracking of Devilry with 
Sentry is to use `Sentry's official Django integration <https://docs.sentry.io/platforms/python/guides/django/>`_.

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


***********************************
Configure deeper sentry integration
***********************************

If you want to report errors that use the devilry reporting module (background tasks, etc.),
you should add this to setings::

    DEVILRY_ERROR_REPORTER_CLASS = "devilry.utils.report_error.SentryErrorReporter"
    # .. or if you want errors in both logs and Sentry:
    # DEVILRY_ERROR_REPORTER_CLASS = "devilry.utils.report_error.SentryWithLogsErrorReporter"


To test that the setup is working, you can use the following management command::

    $ cd ~/devilrydeploy/
    $ venv/bin/python manage.py devilry_test_rq_task fail --queue default --userid <user_id>

See :doc:`rq` for more information about the management command.



***********
Whats next?
***********
After setting up Sentry you might also want to configure Devilry's logging:

- :doc:`logging`.
