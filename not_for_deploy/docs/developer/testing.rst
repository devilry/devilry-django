########################
How to unit-test Devilry
########################

This guide explains how to test Devilry.


*************
Running tests
*************

Run **all** test::

    $ pytest devilry
    ... or ...:
    $ DJANGOENV=test python manage.py test devilry

Run only some tests::

    $ pytest devilry/devilry_examiner/tests/
    ... or ...:
    $ DJANGOENV=test python manange.py test devilry.devilry_examiner.tests


.. warning::
    We use ``DJANGOENV=test python manage.py`` to run tests, because that makes
    ``manage.py`` use ``devilry.project.develop.settings.test``,
    which does not run migrations.

    If you are using PyCharm or another IDE, make sure it runs tests with
    this environment variable set. In PyCharm, you do this by going to:

    - ``Run -> Edit configurations``
    - Expand "Django tests", and remove all the faded out tests below "Django tests"
      (if you do not do this the new environment variable will not be applied to those tests).
    - Expand "Defaults", select "Django tests", and add ``DJANGOENV=test`` to the
      environment setting.


*************
Mocking tests
*************
Always try to mock objects instead of creating real data unless you are actually testing
something that needs real data. Use https://pypi.python.org/pypi/mock to mock your
tests.


***********
Testhelpers
***********
Devilry has several generations of helpers that helps with
building the devilry data structures:

- :ref:`Model bakery recipes <modelbakeryrecipes>`. **This should be used for all new tests**.
- :doc:`devilry.project.develop.teshelpers.corebuilder <devilry.project.develop.teshelpers.corebuilder>`.
  Used in a large percentage of our tests.
  *Should not be used for new tests*.


.. _modelbakeryrecipes:

********************
Model bakery recipes
********************

.. currentmodule:: devilry.apps.core.baker_recipes

`Model bakery`_ is a great library for building Django data models
in tests. It makes it easy to write tests where you only need to
specify data relevant for the test. This makes tests far more readable,
since you always know that any created data models and the specified
attributes are needed to setup data for the specific scenario tested by the
test.

Handling time
=============
For a lot of cases, simply using ``baker.make()`` is enough, but Devilry has
a recursive hierarchi where time matters. To make this easier to handle,
we have a set of model baker recipes that that we use to create the objects that require
date/time. The old test helpers used relative time to solve the challenge of building
:class:`devilry.apps.core.models.Period` and :class:`devilry.apps.core.models.Assignment`
objects, but the model baker recipes solves this in a more elegant manner.

We define 3 distincs periods of time: old, active and future:

    Old
        The *old* time period lasts from *1000-01-01 00:00* to *1999-12-31 23:59:59*.
    Active
        The *active* time period lasts from *2000-01-01 00:00* to *5999-12-31 23:59:59*.
    Future
        The *future* time period lasts from *6000-01-01 00:00* to *9999-12-31 23:59:59*.

.. note::

    Since the time periods are so enourmously large, we do not (for most tests)
    need to use relative time. As long as we use dates so far in the future
    that they will not break within any feasable life span for Devilry,
    we can safely use a normal ``datetime.datetime``, such as ``datetime.datetime(3500, 1, 1)``
    when we need to test assignment publishing times or deadlines that we need
    to be in the future. For the most part, creating a ``datetime.datetime`` object is not
    needed since we have variables and recipes to express the most common use cases.


We have recipes for creating a period spanning each of these time periods:

- :obj:`devilry.apps.core.baker_recipes.period_old`
- :obj:`devilry.apps.core.baker_recipes.period_active`
- :obj:`devilry.apps.core.baker_recipes.period_future`

And we have recipes for creating assignments at the beginning, middle and end of the
these time periods:

Old:
    - :obj:`devilry.apps.core.baker_recipes.assignment_oldperiod_start`
    - :obj:`devilry.apps.core.baker_recipes.assignment_oldperiod_middle`
    - :obj:`devilry.apps.core.baker_recipes.assignment_oldperiod_end`
Active:
    - :obj:`devilry.apps.core.baker_recipes.assignment_activeperiod_start`
    - :obj:`devilry.apps.core.baker_recipes.assignment_activeperiod_middle`
    - :obj:`devilry.apps.core.baker_recipes.assignment_activeperiod_end`
Future:
    - :obj:`devilry.apps.core.baker_recipes.assignment_futureperiod_start`
    - :obj:`devilry.apps.core.baker_recipes.assignment_futureperiod_middle`
    - :obj:`devilry.apps.core.baker_recipes.assignment_futureperiod_end`

Furthermore, we have defined a set of variables that define the
bounds of the old, active and future time periods. These are very useful
when we just need to use a datetime within the bounds a time period:

.. autosummary::

    OLD_PERIOD_START
    OLD_PERIOD_END
    ACTIVE_PERIOD_START
    ACTIVE_PERIOD_END
    FUTURE_PERIOD_START
    FUTURE_PERIOD_END
    ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE
    ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME
    ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE
    ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME



****************
Bakery factories
****************
We also provide some factory functions for very common cases. These factory functions
are just thin wrappers around ``baker.make``.


Factory functions for candidates and examiners
==============================================

Example::

    testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
    devilry_core_baker_factories.candidate(group=testgroup, shortname='user1',
                                           fullname='Test User 1',
                                           automatic_anonymous_id='Loki')
    devilry_core_baker_factories.examiner(group=testgroup, shortname='user1')

As you can see these factories are fairly limited, but they are very nice
when you just need an examiner or candidate.


***************************************
When NOT to use the model baker recipes
***************************************
Do not use the recipes when the things they setup do not matter. For example,
if the code just needs an Assignment object, and the period, publishing time,
and first deadline does not matter, simpy use ``baker.make('core.Assignment')``.


************************************
Bakery recipes and factories apidocs
************************************

.. automodule:: devilry.apps.core.baker_recipes
    :members:

.. automodule:: devilry.apps.core.devilry_core_baker_factories
    :members:


***************************
Testing formatted date/time
***************************
When writing tests for rendering of formatted datetime, you should
override the date formatting setting to ensure your tests are not
broken by changes to the date/time formatting settings::

    class MyTestCase(TestCase):
        def test_something(self):
            with self.settings(DATETIME_FORMAT='Y-m-d H:i', USE_L10N=False):
                ...

Since using iso format with DATETIME_FORMAT is convenient, we provide
:obj:`devilry.utils.datetimeutils.ISODATETIME_DJANGOFORMAT`, which you can use
in the tests::

    class MyTestCase(TestCase):
        def test_something(self):
            with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
                ...

********
Examples
********

Create a period that is active now::

    period = baker.make_recipe('devilry.apps.core.period_active')

Create an assignment that is within an active period, but with
publishing time and first deadline in the past::

    assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

Create 3 assignments within the same active period, one at the beginning, one in the middle and
one at the end. Both the middle and end assignments will have publishin time and first deadline
in the future (by over a 1000 years)::

    period = baker.make_recipe('devilry.apps.core.period_active')
    assignment1 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                    parentnode=period)
    assignment2 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_middle',
                                    parentnode=period)
    assignment3 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                                    parentnode=period)

You can specify attributes with the recipes, so to create an assignment
within an active period, with subject name set to "Test course 101",
period name set to "Some semester", and assignment name set to "Testassignment", use
one of the ``assignment_activeperiod_*`` recipes like this::

    assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                   parentnode__parentnode__long_name='Test course 101',
                                   parentnode__long_name='Some semester',
                                   long_name='Testassignment')


Creating an assignment with assignmentgroups and examiners::

    assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

    # Adding an AssignmentGroup with a single candidate.
    baker.make('core.Candidate', assignment_group__parentnode=assignment)

    # Multiple candidates in one group require a bit more code
    group = baker.make('core.AssignmentGroup', parentnode=assignment)
    baker.make('core.Candidate',
               assignment_group=group,
               student__shortname='student1')
    baker.make('core.Candidate',
               assignment_group=group,
               student__shortname='student2')

    # We just need a lot of AssignmentGroup objects
    # ... without candidates:
    baker.make('core.AssignmentGroup', parentnode=assignment, _quantity=100)
    # ... with candidates:
    baker.make('core.Candidate', assignment_group__parentnode=assignment, _quantity=100)

    # Adding examiners is just like adding candidates,
    # except that the assignment group foreignkey is called ``assignmentgroup``
    # instead of ``assignment_group``, and the user foreignkey is called ``user``
    # instead of ``student``.
    baker.make('core.Examiner', assignmentgroup__parentnode=assignment,
               user__shortname='examiner1')

Creating a period with RelatedStudent and RelatedExaminer objects::

    period = baker.make_recipe('devilry.apps.core.period_active')
    baker.make('core.RelatedStudent', period=period, user__shortname='student1')
    baker.make('core.RelatedStudent', period=period, user__shortname='student2')
    baker.make('core.RelatedExaminer', period=period, user__shortname='examiner1')


Adding admins::

    # Creating a node with an admin
    node = baker.make('core.Node', admins=[baker.make('devilry_account.User')])

    # Adding admins to the parentnode without creating a separate parentnode
    subject = baker.make('core.Subject', parentnode__admins=[baker.make('devilry_account.User')])

    # Combining this with the recipes for creating periods (same for other recipes).
    # - Lets create a period with an admin, and with an admin on the subject and on the
    #   parentnode of the subject.
    period = baker.make_recipe('devilry.apps.core.period_active',
        admins=[baker.make('devilry_account.User', shortname='periodadmin')],
        parentnode__admins=[baker.make('devilry_account.User', shortname='subjectadmin')],
        parentnode__parentnode__admins=[baker.make('devilry_account.User', shortname='nodeadmin')],
    )


.. _`Model bakery`: http://model-bakery.readthedocs.org
