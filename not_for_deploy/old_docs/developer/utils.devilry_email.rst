.. _devilry.utils.devilry_email:

==========================================================
:mod:`devilry.utils.devilry_email`
==========================================================

.. py:exception:: NoEmailAddressException

    Raised when email adress is missing on users.   

.. py:function:: send_email(user_objects_to_send_to, subject, message)

   Send email to the list of users in user_objects_to_send_to

.. py:function:: send_email_admins(subject, message, fail_silently=False)

   Send email to admins registered in settings.ADMINS.

