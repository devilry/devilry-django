************************************************************
corebuilder --- Setup devilry core data structures for tests
************************************************************

.. module:: devilry.project.develop.testhelpers.corebuilder

:mod:`devilry.project.develop.testhelpers.corebuilder` is a module that makes it easy to create :mod:`devilry.apps.core.models` data for
tests.


When to use
===========
Use this for end-to-end tests and tests where you really need real data. Always
try to mock objects instead of creating real data unless you are actually testing
something that needs real data. See :doc:`mock`.

Howto
=====
Each class in the core has a wrapper class in
:mod:`devilry.project.develop.testhelpers.corebuilder` that makes it easy to perform
operations that we need to setup tests. We call these wrappers *builders*, and
they are all prefixed with the name of their corresponding core model and
suffixed with ``Builder``.

Using the builders is very easy::

    from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
    duck1010builder = NodeBuilder('duckuniversity').add_subject('duck1010')
    assert(duck1010builder.subject == Subject.objects.get(short_name='duck1010'))

They can all easily be updated with new attributes::

    duck1010builder.update(long_name='DUCK1010 - Programming')
    assert(duck1010builder.subject.long_name == 'DUCK1010 - Programming')

And they have sane defaults optimized for testing, so you can easily create a
deeply nested core object. This creates the duck1010-subject with an active
period that started 3 months ago and ends in 3 months, with a single assignment
(week1), with a single group, with deadline one week from now with a single
``helloworld.txt`` delivery::

    from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
    from devilry.project.develop.testhelpers.corebuilder import UserBuilder
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

    from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
    from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
    duck1010_builder = SubjectBuilder.quickadd_ducku_duck1010()
    currentperiod_builder = PeriodBuilder.quickadd_ducku_duck1010_active()


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
- Time of delivery (for :class:`DeliveryBuilder` and :meth:`DealdineBuilder.add_delivery`)
  default to *now*.
- Default ``publishing_time`` for assignments is *now*.
- UserBuilder defaults to setting email to ``<username>@example.com``.

These defaults are all handled in the constructor of their builder-class. All
the defaults can be overridden by specifying a value for them.


Reload from DB
==============
You often need to create an object that is changed by
the code you are testing, and then check that
the change has made it to the database. All our builders implement
:class:`ReloadableDbBuilderInterface` which includes
:meth:`~ReloadableDbBuilderInterface.reload_from_db`.




ReloadableDbBuilderInterface
============================

.. py:class:: ReloadableDbBuilderInterface

    All the builders implement this interface.

    .. py:method:: update(**attributes)

        Update the object wrapped by the builder with the given attributes.
        Saves the object, and reloads it from the database.

    .. py:method:: reload_from_db(**attributes)

        Reloads the object wrapped by the builder from the database.
        Perfect when you create an object that is changed by
        the code you are testing, and you want to check that
        the change has made it to the database.


UserBuilder
===========
.. py:class:: UserBuilder

    Creates a User object for testing. Also creates the DevilryUserProfile,
    and methods for editing both the User and the profile.

    .. py:method:: __init__(username, full_name=None, email=None)

        Creates a new User with password set to test, and the
        :class:`devilry.apps.core.models.DevilryUserProfile` created.

        :param username: The username of the new user.
        :param full_name: Optional full_name. Defaults to ``None``.
        :param email: Optional email. Defaults to ``<username>@example.com``.

    .. py:method:: update(**attributes)

        Update the User with the given attributes.
        Reloads the object from the database.

    .. py:method:: update_profile(**attributes)

        Update the :class:`devilry.apps.core.models.DevilryUserProfile`
        with the given attributes. Reloads the object from the database.


NodeBuilder
===========
.. py:class:: NodeBuilder

    .. py:attribute:: node

        The :class:`~devilry.apps.core.models.Node` wrapped by this builder.

    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Node` with the given attributes.

        :param short_name: The ``short_name`` of the Node.
        :param long_name: The ``long_name`` of the Node. Defaults to ``short_name`` if ``None``.
        :param kwargs: Other arguments for the Node constructor.

    .. py:method:: add_node(*args, **kwargs)

        Adds a childnode to the node. ``args`` and ``kwargs`` are forwarded
        to :class:`.NodeBuilder` with ``kwargs['parentnode']`` set to
        this  :obj:`.node`.

        :rtype: :class:`.NodeBuilder`.

    .. py:method:: add_subject(*args, **kwargs)

        Adds a subject to the node. ``args`` and ``kwargs`` are forwarded
        to :class:`.SubjectBuilder` with ``kwargs['parentnode']`` set to
        this  :obj:`.node`.

        :rtype: :class:`.SubjectBuilder`.


SubjectBuilder
==============
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

        :rtype: :class:`.PeriodBuilder`.


    .. py:method:: add_6month_active_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time`` ``3*30``
        days ago, and ``end_time`` in ``3*30`` days. ``args`` and ``kwargs``
        is forwarded to ``add_period``, but with ``start_time`` and
        ``end_time`` set in ``kwargs``.

        If no ``short_name`` is provided, it defaults to ``active``.

        :rtype: :class:`.PeriodBuilder`.


    .. py:method:: add_6month_lastyear_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time``
        ``365-30*3`` days ago, and ``end_time`` ``365+3*30`` days ago.
        ``args`` and ``kwargs`` is forwarded to ``add_period``, but with
        ``start_time`` and ``end_time`` set in ``kwargs``.

        If no ``short_name`` is provided, it defaults to ``lastyear``.
        :rtype: :class:`.PeriodBuilder`.


    .. py:method:: add_6month_nextyear_period(*args, **kwargs)

        Shortcut for adding :meth:`.add_period` with ``start_time`` in
        ``365-30*3`` days, and ``end_time`` in ``365+3*30`` days. ``args`` and
        ``kwargs`` is forwarded to ``add_period``, but with ``start_time`` and
        ``end_time`` set in ``kwargs``.

        If no ``short_name`` is provided, it defaults to ``nextyear``.

        :rtype: :class:`.PeriodBuilder`.


PeriodBuilder
=============
.. py:class:: PeriodBuilder

    .. py:attribute:: period

        The :class:`~devilry.apps.core.models.Period` wrapped by this builder.

    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Period` with the given attributes.

        :param short_name: The ``short_name`` of the Period.
        :param long_name: The ``long_name`` of the Period. Defaults to ``short_name`` if ``None``.
        :param kwargs: Other arguments for the Period constructor.

    .. py:method:: add_assignment(*args, **kwargs)

        Adds an assignment to the period. ``args`` and ``kwargs`` are forwarded
        to :class:`.AssignmentBuilder` with ``kwargs['parentnode']`` set to
        this :obj:`.period`.

        :rtype: :class:`.AssignmentBuilder`.

    .. py:classmethod:: quickadd_ducku_duck1010_active()

        When we need just a single active period, we use this shortcut
        method instead of writing::

            NodeBuilder('ducku').add_subject('duck1010').add_6month_active_period('current')

        This is not just to save a couple of letters, but also to
        promote a common setup for simple tests.



AssignmentBuilder
=================
.. py:class:: AssignmentBuilder

    .. py:attribute:: assignment

        The :class:`~devilry.apps.core.models.Assignment` wrapped by this builder.

    .. py:method:: __init__(short_name, long_name=None, **kwargs)

        Creates a new :class:`~devilry.apps.core.models.Assignment` with the given attributes.

        :param short_name: The ``short_name`` of the Assignment.
        :param long_name: The ``long_name`` of the Assignment. Defaults to ``short_name`` if ``None``.
        :param publishing_time: The ``publishing_time`` of the Assignment. Defaults to now.
        :param kwargs: Other arguments for the Assignment constructor.

    .. py:method:: add_group(*args, **kwargs)

        Adds an assignment group to the period. ``args`` and ``kwargs`` are forwarded
        to :class:`.AssignmentGroupBuilder` with ``kwargs['parentnode']`` set to
        this :obj:`.assignment`.

        :rtype: :class:`.AssignmentGroupBuilder`.



AssignmentGroupBuilder
======================
.. py:class:: AssignmentGroupBuilder

    .. py:attribute:: assignment_group

        The :class:`~devilry.apps.core.models.AssignmentGroup` wrapped by this builder.

    .. py:method:: __init__(students=[], candidates=[], examiners=[], **kwargs)

        Creates a new :class:`~devilry.apps.core.models.AssignmentGroup` with the given attributes.

        :param students: Forwarded to :meth:`add_students`.
        :param candidates: Forwarded to :meth:`add_candidates`.
        :param examiners: Forwarded to :meth:`add_examiners`.
        :param kwargs: Arguments for the AssignmentGroup constructor.

    .. py:method:: add_students(*users)

        Add the given users as candidates without a candidate ID on this assignment group.

        :return: ``self`` (to enable us to nest the method call).

    .. py:method:: add_examiners(*users)

        Add the given users as examiners on this assignment group.

        :return: ``self`` (to enable us to nest the method call).

    .. py:method:: add_students(*candidates)

        Add the given candidates to this assignment group.
        
        :param candidates: :class:`devilry.apps.core.models.Candidate` objects.
        :return: ``self`` (to enable us to nest the method call).

    .. py:method:: add_deadline(*args, **kwargs)

        Adds an deadline to the assignment. ``args`` and ``kwargs`` are forwarded
        to :class:`.DeadlineBuilder` with ``kwargs['assignment_group']`` set to
        this :obj:`.assignment_group`.

        :rtype: :class:`.AssignmentGroupBuilder`.

    .. py:method:: add_deadline_in_x_weeks(weeks, *args, **kwargs)

        Calls :meth:`.add_deadline` with ``kwargs[deadline]`` set
        ``weeks`` weeks in the future.

        :rtype: :class:`.AssignmentGroupBuilder`.

    .. py:method:: add_deadline_x_weeks_ago(weeks, *args, **kwargs)

        Calls :meth:`.add_deadline` with ``kwargs[deadline]`` set
        ``weeks`` weeks in the past.

        :rtype: :class:`.DeadlineBuilder`.


DeadlineBuilder
===============
.. py:class:: DeadlineBuilder

    .. py:attribute:: deadline

        The :class:`~devilry.apps.core.models.Deadline` wrapped by this builder.

    .. py:method:: __init__(**kwargs)

        Creates a new :class:`~devilry.apps.core.models.AssignmentGroup` with the given attributes.

        :param kwargs: Arguments for the Deadline constructor.

    .. py:method:: add_delivery(**kwargs)

        Adds a delivery to the deadline. ``args`` and ``kwargs`` are forwarded
        to :class:`.DeliveryBuilder` with ``kwargs['deadline']`` set to
        this :obj:`.deadline` and ``kwargs['successful']`` defaulting to ``True``.

        :param kwargs: Extra kwargs for the :class:`.DeliveryBuilder` constructor.
        :rtype: :class:`.DeliveryBuilder`.

    .. py:method:: add_delivery_after_deadline(timedeltaobject, **kwargs)

        Add a delivery ``timedeltaobject`` time after this deadline expires.

        Shortcut that calls :meth:`.add_delivery` with ``kwargs['time_of_delivery']`` set
        to ``deadline.deadline + timedeltaobject``.

        Example - add delivery 3 weeks and 2 hours after deadline::

            from datetime import datetime, timedelta
            deadlinebuilder = DeadlineBuilder(deadline=datetime(2010, 1, 1))
            deadlinebuilder.add_delivery_after_deadline(timedelta(weeks=3, hours=2))

        :param kwargs: Extra kwargs for the :class:`.DeliveryBuilder` constructor.
        :rtype: :class:`.DeliveryBuilder`.

    .. py:method:: add_delivery_before_deadline(timedeltaobject, **kwargs)

        Add a delivery ``timedeltaobject`` time before this deadline expires.

        Shortcut that calls :meth:`.add_delivery` with ``kwargs['time_of_delivery']`` set
        to ``deadline.deadline + timedeltaobject``.

        Example - add delivery 5 hours before deadline::

            from datetime import datetime, timedelta
            deadlinebuilder = DeadlineBuilder(deadline=datetime(2010, 1, 1))
            deadlinebuilder.add_delivery_before_deadline(timedelta(hours=5))

        :param kwargs: Extra kwargs for the :class:`.DeliveryBuilder` constructor.
        :rtype: :class:`.DeliveryBuilder`.

    .. py:method:: add_delivery_x_hours_after_deadline(timedeltaobject, **kwargs)

        Add a delivery ``hours`` hours after this deadline expires.

        Shortcut that calls :meth:`.add_delivery_after_deadline` with
        timedeltaobject set to ``timedelta(hours=hours)``.

        :param hours: Number of hours.
        :param kwargs: Extra kwargs for the :class:`.DeliveryBuilder` constructor.
        :rtype: :class:`.DeliveryBuilder`.

    .. py:method:: add_delivery_x_hours_before_deadline(timedeltaobject, **kwargs)

        Add a delivery ``hours`` hours before this deadline expires.

        Shortcut that calls :meth:`.add_delivery_before_deadline` with
        timedeltaobject set to ``timedelta(hours=hours)``.

        :param hours: Number of hours.
        :param kwargs: Extra kwargs for the :class:`.DeliveryBuilder` constructor.
        :rtype: :class:`.DeliveryBuilder`.



DeliveryBuilder
===============
.. py:class:: DeliveryBuilder

    .. py:attribute:: delivery

        The :class:`~devilry.apps.core.models.Delivery` wrapped by this builder.

    .. py:method:: __init__(**kwargs)

        Creates a new :class:`~devilry.apps.core.models.Delivery` with the given attributes.
        If ``time_of_delivery`` is not provided, it defaults to *now*.

        :param kwargs: Arguments for the Delivery constructor.

    .. py:method:: add_filemeta(**kwargs)

        Adds a filemeta to the delivery. ``kwargs`` is forwarded
        to :class:`.FilteMetaBuilder` with ``kwargs['delivery']`` set to
        this :obj:`.delivery`.

        Example::

            deliverybuilder.add_filemeta(
                filename='test.txt',
                data='This is a test.'
            )

        :param kwargs: Kwargs for the :class:`.FileMetaBuilder` constructor.
        :rtype: :class:`.FileMetaBuilder`.

    .. py:method:: add_feedback(**kwargs)

        Adds a feedback to the delivery. ``kwargs`` is forwarded to
        :class:`.StaticFeedbackBuilder` with ``kwargs['delivery']`` set to
        this :obj:`.delivery`.

        Example::

            deliverybuilder.add_feedback(
                points=10,
                grade='10/100',
                is_passing_grade=False,
                saved_by=UserBuilder('testuser').user
            )

        :param kwargs: Kwargs for the :class:`.StaticFeedbackBuilder` constructor.
        :rtype: :class:`.StaticFeedbackBuilder`.

    .. py:method:: add_passed_feedback(**kwargs)

        Shortcut that adds a passed feedback to the delivery. ``kwargs`` is
        forwarded to :meth:`.add_feedback` with:

        - ``points=1``
        - ``grade="Passed"``
        - ``is_passing_grade=True``

        Example::

            deliverybuilder.add_passed_feedback(saved_by=UserBuilder('testuser').user)

        :param kwargs:
            Extra kwargs for :meth:`.add_feedback`. Is updated with
            :points, grade and is_passing_grade as documented above.
        :rtype: :class:`.StaticFeedbackBuilder`.

    .. py:method:: add_failed_feedback(**kwargs)

        Shortcut that adds a failed feedback to the delivery. ``kwargs`` is
        forwarded to :meth:`.add_feedback` with:

        - ``points=0``
        - ``grade="Failed"``
        - ``is_passing_grade=False``

        Example::

            deliverybuilder.add_failed_feedback(saved_by=UserBuilder('testuser').user)

        :param kwargs:
            Extra kwargs for :meth:`.add_feedback`. Is updated with
            :points, grade and is_passing_grade as documented above.
        :rtype: :class:`.StaticFeedbackBuilder`.



FileMetaBuilder
===============
.. py:class:: FileMetaBuilder

    .. py:attribute:: filemeta

        The :class:`~devilry.apps.core.models.FileMeta` wrapped by this builder.

    .. py:method:: __init__(delivery, filename, data)

        Creates a new :class:`~devilry.apps.core.models.FileMeta`. Since FileMeta
        just points to files on disk,  and creating those files requires iterators
        and extra stuff that is almost never needed for tests, we provide an
        easier method for creating files with FileMetaBuilder.

        :param delivery: The Delivery object.
        :param filename: A filename.
        :param data: The file contents as a string.



StaticFeedbackBuilder
=====================
.. py:class:: StaticFeedbackBuilder

    .. py:attribute:: feedback

        The :class:`~devilry.apps.core.models.StaticFeedback` wrapped by this builder.

    .. py:method:: __init__(**kwargs)

        Creates a new :class:`~devilry.apps.core.models.StaticFeedback` with the given attributes.

        :param kwargs: Arguments for the StaticFeedback constructor.
