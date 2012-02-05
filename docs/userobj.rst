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
:class:`devilry.apps.core.models.DevilryUserProfile`. The profile object is
available through the ``devilryuserprofile`` attribute of any
django.contrib.auth.models.User_ object in devilry. It can be used in queries
just like any other one-to-one relation, like this::

    from django.contrib.auth.models import User
    supermen = User.objects.filter(devilryuserprofile__full_name__contains="Superman")


.. _django.contrib.auth.models.User: http://docs.djangoproject.com/en/dev/topics/auth/#users
