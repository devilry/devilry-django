######################################################
Autoset email from the authentication backend username
######################################################

If you have an authentication backend that uses username,
and it does not set an email for your users, you will
probably want to add the ``devilry.devilry_autoset_empty_email_by_username``
app to automatically set an email based on usernames.

To enable this app, add the following to your ``~/devilrydeploy/devilry_settings.py``::

    INSTALLED_APPS += ['devilry.apps.autoset_empty_email_by_username']

    #: Email pattern. The 'devilry.devilry_autoset_empty_email_by_username' app
    #: automatically sets email to "<username>@DEVILRY_DEFAULT_EMAIL_SUFFIX"
    #: when a user is saved.
    DEVILRY_DEFAULT_EMAIL_SUFFIX = 'example.com'
