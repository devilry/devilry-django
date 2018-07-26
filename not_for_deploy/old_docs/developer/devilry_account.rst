########################################################
:mod:`devilry_account` --- User account models and views
########################################################

The ``devilry_account`` module takes care of autentication,
user profile editing, user profile creation, etc.


****************************
About the devilry User model
****************************
Devilry uses a completely custom Django user model:

- It does not have the permission framework.
- Only superusers get access to the Django admin UI.
- We use full names instead of separate ``first_name`` and
  ``last_name`` fields, but we store the last name to make
  it possible to sort on that.
- We support multiple usernames for each user (only used when
  the authentication backend uses usernames).
- We support multiple email addresses per user.
- We do not use a boolean field for ``is_active``. Instead we
  handle this via a ``suspended_datetime`` field, and we have
  a field where reason for suspension can be set.
- We have a field for storing the preferred language of the user.


*************
Datamodel API
*************
The data models was introduced by :devilryissue:`780`.

.. currentmodule:: devilry.devilry_account.models

.. automodule:: devilry.devilry_account.models
    :members:
