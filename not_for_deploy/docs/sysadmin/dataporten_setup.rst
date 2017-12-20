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


********************************
Use username instead of feide ID
********************************
By default, we use the ``userid_sec`` field from Dataporten as the
"shortname" for users. This field is not very pretty, but it is unique.
This means that the shortname which is used some places in the UI, looks
something like this: ``feide:myuser@uio.no``.

You can change this to just ``myuser`` (the username part) for a single
``userid_sec`` suffix with the ``DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX``
setting. For example::

    DEVILRY_FEIDE_USERID_SEC_TO_USERNAME_SUFFIX = 'uio.no'

If you forget this, and set it later, the shortname of users will
be updated the next time they login.
