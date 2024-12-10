===========================================
Migrating from 3.3.5 to 6.3.6
===========================================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

Added new ``DEVILRY_SKIP_CSRF_FOR_APIVIEWS`` setting::


    # Can be used when you have a proxy that has issues with csrftoken Cookie AND
    # you have checks in the proxy that prevents browsers without support for SameSite
    # AND you have the ``SESSION_COOKIE_SAMESITE="Lax"`` or ``SESSION_COOKIE_SAMESITE="Strict"``.
    # This disables CSRF checks for APIs that is used by the javascript code in the UI.
    DEVILRY_SKIP_CSRF_FOR_APIVIEWS = False

Defaults to ``False``.


Update devilry to 6.3.6
##############################

Update the devilry version to ``3.3.5`` as described in :doc:`../update`.

