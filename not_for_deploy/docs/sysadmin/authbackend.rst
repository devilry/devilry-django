######################################
Setup a Devilry authentication backend
######################################

*******
Choices
*******
Devilry can work with any Django-compatible authentication backend.


**********************************
The default authentication backend
**********************************
If you do not have a user database that you wish to use for Devilry, you can use
the default Django authentication backend, and add users to Devilry
manually.


***********************
Authenticate using LDAP
***********************
Authenticating via LDAP requires the ``django-auth-ldap`` Python module and some small adjustments to your settings.


Install the django-auth-ldap module
===================================
Add a new line containing ``django-auth-ldap`` in your ``~/devilrydeploy/requirements.txt``,
then run::

    $ cd ~/devilrydeploy
    $ venv/bin/pip install -r requirements.txt

to install the new module.


Add the LDAP backend to your settings
=====================================
Add the following to your ``~/devilrydeploy/devilry_settings.py``::

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
    )

You will also have to configure how to authenticate via LDAP. That is explained in
the django-auth-ldap docs: https://pythonhosted.org/django-auth-ldap/authentication.html


*************
Autoset email
*************
If your authentication backend does not provide an email address for your users, you
will most likely want to take a look at: :doc:`autoset_empty_email_by_username`.
