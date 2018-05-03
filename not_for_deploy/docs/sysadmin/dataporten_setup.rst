##########################################
How to setup Dataporten (Feide etc.) login
##########################################


********
Settings
********
Make sure your ``AUTHENTICATION_BACKENDS`` setting includes
``"allauth.account.auth_backends.AuthenticationBackend"``.

Example::

    INSTALLED_APPS += [
        'devilry.devilry_dataporten_allauth',
    ]

    AUTHENTICATION_BACKENDS = [
        'allauth.account.auth_backends.AuthenticationBackend',
    ]


You can have more authentication backends than just the _allauth_
backend, but if you only have the allauth backend, login will
redirect directly to dataporten for login instead of asking users
how they wish to sign in.


********************************
Setup the dataporten application
********************************

Go to https://dashboard.dataporten.no/, and create a new application.
You probably want to create the application within an organization instead
of a personal app, but for local testing, a personal app should work.

In the create new application popup
===================================

- **Name**: Whatever you want (Typically: "Devilry", "My Devilry test", etc.)
- **OAuth 2.0 Redirect URL**: ``https://<devilry domain>/authenticate/allauth/dataporten/login/callback/``.
  E.g.: https://devilry.example.com/authenticate/allauth/dataporten/login/callback/. For localhost
  development, you can use ``localhost:8000`` as the ``<devilry domain>``, and http instead of https.


Within the application dashboard
================================

Permissions
-----------
Devilry requires that you include the following scopes:

- Profilinfo
- Bruker-ID
- E-post
- Feide-navn


Auth providers
--------------
You will most likely want to deselect: *Accept all social networks*,
*Feide gjestebrukere* and *Feide testbrukere*. For testing purposes,
*Feide testbrukere* may be useful, but not for production.

You will most likely want to deselect *Åpne for alle i utdanningsektoren*, and
just select the relevant schools.



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

    You find the credentials for your app via https://dashboard.dataporten.no
    (in the *OAuth credentials* section).


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
