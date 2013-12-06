************************************************
:mod:`devilry_developer.testhelpers.corebuilder`
************************************************

.. warning:: This module is under development.

.. module:: devilry_developer.testhelpers.corebuilder


A module that makes it easy to create :mod:`devilry.apps.core.models` data for
tests.

Howto
=====
Each class in the core has a wrapper class in
:mod:`devilry_developer.testhelpers.corebuilder` that makes it easy to perform
operations that we need to setup tests. We call these wrappers *builders*, and
they are all prefixed with the name of their corresponding core model and
suffixed with ``Builder``.

Using the builders is very easy::

    duck1010builder = NodeBuilder('duckuniversity').add_subject('duck1010')
    assert(duck1010builder.subject == Subject.objects.get(short_name='duck1010'))

They can all easily be updated with new attributes::

    duck1010builder.update(long_name='DUCK1010 - Programming')
    assert(duck1010builder.subject.short_name == 'duck1010')

And they have sane defaults optimized for testing, so you can easily create a
deeply nested core object. This creates the duck1010-subject with an active
period that started 3 months ago and ends in 3 months, with a single assignment
(week1), with a single group, with deadline one week from now with a single
``helloworld.txt`` delivery::

    peterpan = UserBuilder(username='peterpan')
    NodeBuilder('duckuniversity')\
        .add_subject('duck1010')\
        .add_6month_active_period('current')\
        .add_assignment('week1')\
        .add_group(students=[peterpan.user])\
        .add_deadline_in_x_weeks(weeks=1)\
        .add_delivery()\
        .add_filemeta(filename='helloworld.txt', data='Hello world')




Magic and defaults
==================
The builders have very little magic, but they have some defaults that make
sense when testing:

- ``long_name`` is set to ``short_name`` when it is not specified explicitly.
- All BaseNodes (the models with short and long name) takes the ``short_name``
  as the first argument and the ``long_name`` as the second argument.
- Time of delivery (for ``add_delivery()``) default to *now*. Use
  ``add_delivery_after_deadline`` and ``add_delivery_before_deadline`` for more
  control.
- Default ``publishing_time`` for assignments is *now*.
- UserBuilder defaults to setting email to ``<username>@example.com``.

These defaults are all handled in the constructor of their builder-class. All
the defaults can be overridden by specifying a value for them.



.. py:class:: NodeBuilder

    TODO
