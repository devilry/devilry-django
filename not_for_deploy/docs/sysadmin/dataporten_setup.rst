##########################################
How to setup Dataporten (Feide etc.) login
##########################################


********
Settings
********
Make sure your ``AUTHENTICATION_BACKENDS`` setting includes
``"allauth.account.auth_backends.AuthenticationBackend"`.

Example::

    INSTALLED_APPS += [
        'allauth.socialaccount.providers.dataporten',
    ]

    AUTHENTICATION_BACKENDS = [
        'allauth.account.auth_backends.AuthenticationBackend',
    ]


You can have more authentication backends than just the _allauth_
backend, but if you only have the allauth backend, login will
redirect directly to dataporten for login instead of asking users
how they wish to sign in.


*********************************
Add required data to the database
*********************************

Setup your primary domain with::

    $ python manage.py devilry_setup_primary_domain <your domain here>
    $ ... E.g.:
    $ python manage.py devilry_setup_primary_domain devilry.example.com


Setup dataporten credentials::

    $ python manage.py devilry_setup_dataporten_provider <OAuth Client credentials>
    $ ... E.g.:
    $ python manage.py devilry_setup_dataporten_provider xxx-xxx-xxx-xxx-xxxxx


.. note::

    You find your credentials via https://dashboard.dataporten.no.
