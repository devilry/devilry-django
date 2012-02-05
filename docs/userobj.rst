.. _userobj:

=============================
The Devilry User object
=============================


Django user
###########

Devilry users are Django django.contrib.auth.models.User_ objects. However we only use a subset of the fields:

- username
- email
- is_superuser
- password (if authenticating using the default Django auth)


Additional data
###############

Additional data is stored in a one-to-one relation to
:class:`devilry.apps.core.models.DevilryUserProfile`.



.. _django.contrib.auth.models.User: http://docs.djangoproject.com/en/dev/topics/auth/#users
