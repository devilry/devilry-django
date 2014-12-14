###################
devilry_useradmin
###################

Provides superadmins the ability to browse and manage users.


Settings
========

This app supports a couple of settings that you can put in your ``settings.py``.

Settings that tune the user/group editor:

    DEVILRY_USERADMIN_USER_READONLY_FIELDS
        A tuple of fields in the ``User`` model/table that should not be editable. Defaults to an empty
        tuple. Example (makes all fields read-only)::

            DEVILRY_USERADMIN_USER_READONLY_FIELDS = ['email', 'is_active', 'is_superuser', 'is_staff', 'is_active']

        Note: ``date_joined`` and ``last_login`` is always read-only. ``username`` and ``password`` can not be read-only.

    DEVILRY_USERADMIN_DEVILRYUSERPROFILE_READONLY_FIELDS
        A tuple of fields in the ``DevilryUserProfile`` model/table that should not be editable. Defaults to::

            DEVILRY_USERADMIN_DEVILRYUSERPROFILE_READONLY_FIELDS = ['languagecode']

        Example (makes all fields read-only)::

            DEVILRY_USERADMIN_DEVILRYUSERPROFILE_READONLY_FIELDS = ['languagecode', 'full_name']

    DEVILRY_USERADMIN_USER_INCLUDE_PERMISSIONFRAMEWORK
        Set this to ``True`` to include the default Django permission
        framework, including the group-manager. This is not used by Devilry,
        however it may be used by other Django apps that extends/work with
        Devilry. Defaults to::

            DEVILRY_USERADMIN_USER_INCLUDE_PERMISSIONFRAMEWORK = False

    DEVILRY_USERADMIN_USER_CHANGE_VIEW_MESSAGE
        A message displayed at the top of the *change user* view. Typically
        used to notify administrators about inconsistencies/special cases when
        syncing devilry with another user database.

    DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE
        Help message for the password field in the *change user* view.

        You can use HTML in the message, however you should limit yourself to
        these tags (I.E.: only inline markup):
        
            strong, em, a

        to avoid messing up the layout.

        Example::

            DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE = 'Passwords are handled by Our Awesome External User Management System. Follow <a href="https://awesome.example.com">this link</a> to reset passwords.'
            

    DEVILRY_USERADMIN_USER_ADD_VIEW_MESSAGE
        A message displayed at the top of the *add user* view. Typically used
        to notify administrators about inconsistencies/special cases when
        syncing devilry with another user database.

    DEVILRY_USERADMIN_USERNAME_EDITABLE
        Configures if usernames are editable or not. This is probably not a
        good idea if you use an external authentication system. Default::

           DEVILRY_USERADMIN_USERNAME_EDITABLE = False 

    DEVILRY_USERADMIN_USERNAME_NOT_EDITABLE_MESSAGE
        The error message displayed when someone tries to edit the username when
        ``DEVILRY_USERADMIN_USERNAME_EDITABLE==False``. Defaults to a translatable
        error message that informs users that the system admin has disabled
        editing of the username, and to contact the system admin if this is a
        problem.


Configure for integration with an external authentication system
================================================================
When using an external authentication system you usually want to use these settings::

    DEVILRY_USERADMIN_USER_CHANGE_VIEW_MESSAGE = 'Explain that users are synced with another system here'
    DEVILRY_USERADMIN_USER_ADD_VIEW_MESSAGE = 'Explain that users are authenticated in another system here, and that adding a new user via the webinterface does not guarantee that the user can log in.'
    DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE = 'Explain how passwords are handled here'


FAQ
===

Why cant I completely remove the password field?
    Because we like to keep the implementation simple, and we think that making
    it possible to inform users that the password can not be changed using
    ``DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE`` is good enough.

Why can I not disable the username field?
    Because we like to keep the implementation simple, and we think that making
    it possible to inform users that the username can not be changed using
    ``DEVILRY_USERADMIN_USERNAME_NOT_EDITABLE_MESSAGE`` is good enough.

Can I translate the custom messages?
    There is no easy way of translating the messages. If you know how, you can
    create a Django app where you add messages marked for translation to
    ``models.py``, and then import them in your ``settings.py``. The easy
    solution is to write them in a language that all of your administrators
    understand.
