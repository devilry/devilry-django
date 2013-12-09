************************************************
Setup devilry core data structures for tests
************************************************

.. module:: devilry_developer.testhelpers.corebuilder

:mod:`devilry_developer.testhelpers.corebuilder` is a module that makes it easy to create :mod:`devilry.apps.core.models` data for
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
    helloworld_filemetabuilder = NodeBuilder('ducku')\
        .add_subject('duck1010')\
        .add_6month_active_period('current')\
        .add_assignment('week1')\
        .add_group(students=[peterpan.user])\
        .add_deadline_in_x_weeks(weeks=1)\
        .add_delivery()\
        .add_filemeta(filename='helloworld.txt', data='Hello world')


Since we often need to add a single subject or a single active period, we have
shortcuts for that::

    duck1010_builder = SubjectBuilder.quickadd_ducku_duck1010()
    currentperiod_builder = PeriodBuilder.quickadd_ducku_duck1010_current()


.. note::

    These shortcuts is not there just to save a couple of keystrokes. They are there
    to make sure we use a uniform test setup in 98% of our tests. As long as you just
    need a single subject or period, you MUST use these shortcuts (to get a patch
    accepted in Devilry).


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

    .. py:attribute:: node

        The :class:`~devilry.apps.core.models.Node` wrapped by this builder.

    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Node` with the given attributes.

        :param short_name: The ``short_name`` of the Node.
        :param long_name: The ``long_name`` of the Node. Defaults to ``short_name`` if ``None``.
        :param kwargs: Other arguments for the Node constructor.

    .. py:method:: add_subject(*args, **kwargs)

        Adds a subject to the node. ``args`` and ``kwargs`` are forwarded
        to :class:`.SubjectBuilder` with ``kwargs['parentnode']`` set to
        this  :obj:`.node`.

        :rtype: :class:`.SubjectBuilder`.


.. py:class:: SubjectBuilder

    .. py:attribute:: subject

        The :class:`~devilry.apps.core.models.Subject` wrapped by this builder.


    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Subject` with the given attributes.

        :param short_name: The ``short_name`` of the Subject.
        :param long_name: The ``long_name`` of the Subject. Defaults to ``short_name`` if ``None``.
        :param kwargs: Other arguments for the Subject constructor.


    .. py:classmethod:: quickadd_ducku_duck1010()

        When we need just a single subject, we use this shortcut
        method instead of writing::

            NodeBuilder('ducku').add_subject('duck1010')

        This is not just to save a couple of letters, but also to
        promote a common setup for simple tests.


    .. py:method:: add_period(*args, **kwargs)

        Adds a period to the subject. ``args`` and ``kwargs`` are forwarded
        to :class:`.PeriodBuilder` with ``kwargs['parentnode']`` set to
        this :obj:`.subject`.

        :rtype: :class:`.SubjectBuilder`.


    .. py:method:: add_6month_active_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time`` ``3*30`` days ago, and ``end_time`` in ``3*30`` days. ``args`` and ``kwargs`` is forwarded to ``add_period``, but with ``start_time`` and ``end_time`` set in ``kwargs``.

        :rtype: :class:`.SubjectBuilder`.


    .. py:method:: add_6month_lastyear_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time`` ``365-30*3`` days ago, and ``end_time`` ``365+3*30`` days ago. ``args`` and ``kwargs`` is forwarded to ``add_period``, but with ``start_time`` and ``end_time`` set in ``kwargs``.

        :rtype: :class:`.SubjectBuilder`.


    .. py:method:: add_6month_nextyear_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time`` in ``365-30*3`` days, and ``end_time`` in ``365+3*30`` days. ``args`` and ``kwargs`` is forwarded to ``add_period``, but with ``start_time`` and ``end_time`` set in ``kwargs``.

        :rtype: :class:`.SubjectBuilder`.


.. py:class:: PeriodBuilder

    .. py:attribute:: period

        The :class:`~devilry.apps.core.models.Period` wrapped by this builder.


    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Period` with the given attributes.

        :param short_name: The ``short_name`` of the Period.
        :param long_name: The ``long_name`` of the Period. Defaults to ``short_name`` if ``None``.
        :param kwargs: Other arguments for the Period constructor.


    .. py:classmethod:: quickadd_ducku_duck1010_current()

        When we need just a single active period, we use this shortcut
        method instead of writing::

            NodeBuilder('ducku').add_subject('duck1010').add_6month_active_period('current')

        This is not just to save a couple of letters, but also to
        promote a common setup for simple tests.

