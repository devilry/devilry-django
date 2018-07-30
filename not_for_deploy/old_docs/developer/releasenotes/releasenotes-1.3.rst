#################
Release Notes 1.3
#################

.. seealso:: :devilrydeploy:`Migration guide for sysadmins <migrationguides/1.3.html>`


*************
Major changes
*************

REST APIs
=========
We are working on migrating from ``djangorestframework`` version 1 to
``django-simple-rest``. The reason for this is that ``djangorestframework``
version 2 is incompatible with version one, but they use the same namespace,
which makes it hard to run them side by side. We could hack it to work, but
``django-simple-rest`` matches our needs better, and it is more in line with
the modern Django view API. We have created the ``devilry_rest`` module
where we keep our common REST utilities, and we have implemented public/private
authentication that will make it a lot easier to program against Devilry.


Fixed HARD deadlines issues
===========================
We have moved all constraint checking for HARD deadlines from the core into the
only view where it makes sense to check for hard deadlines. This view is, of
course, the one where users add deliveries.

This fixes a lot of edge case issues, such as examiners adding a placeholder
delivery when the deadline has expired.

More details: https://github.com/devilry/devilry-django/issues/434


Tell students when they are not relatedstudent on a semester/period
===================================================================
We add a big red message for students when they are not student on a period.
This can happen when students are added to a group, and later removed from the
subject/course.

More details and screenshots: https://github.com/devilry/devilry-django/issues/433


MathJaX embedded
================
We have included MathJaX as part of the Devilry repo.
