from datetime import datetime

from model_mommy import recipe

from devilry.apps.core.models import Period, Assignment


#
#
# Constants for old periods and assignments
#
#

#: The ``start_time`` of the period created by the :obj:`.period_old` recipe.
OLD_PERIOD_START = datetime(1000, 1, 1, 0, 0)

#: The ``end_time`` of the period created by the :obj:`.period_old` recipe.
OLD_PERIOD_END = datetime(1999, 12, 31, 23, 59)

#: The ``first_deadline`` of the assignment created by the
#: :obj:`.assignment_activeperiod_start`.
ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE = datetime(1000, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_oldperiod_end`.
ASSIGNMENT_OLDPERIOD_MIDDLE_PUBLISHING_TIME = datetime(1500, 1, 1, 0, 0)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_oldperiod_end`.
ASSIGNMENT_OLDPERIOD_MIDDLE_FIRST_DEADLINE = datetime(1500, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_oldperiod_end`.
ASSIGNMENT_OLDPERIOD_END_PUBLISHING_TIME = datetime(1999, 12, 1, 0, 0)


#
#
# Constants for active periods and assignments
#
#

#: The ``start_time`` of the period created by the :obj:`.period_active` recipe.
ACTIVE_PERIOD_START = datetime(2000, 1, 1, 0, 0)

#: The ``end_time`` of the period created by the :obj:`.period_active` recipe.
ACTIVE_PERIOD_END = datetime(5999, 12, 31, 23, 59)

#: The ``first_deadline`` of the assignment created by the
#: :obj:`.assignment_activeperiod_start`.
ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE = datetime(2000, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_activeperiod_end`.
ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME = datetime(3500, 1, 1, 0, 0)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_activeperiod_end`.
ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE = datetime(3500, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_activeperiod_end`.
ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME = datetime(5999, 12, 1, 0, 0)


#
#
# Constants for future periods and assignments
#
#

#: The ``start_time`` of the period created by the :obj:`.period_future` recipe.
FUTURE_PERIOD_START = datetime(6000, 1, 1, 0, 0)

#: The ``end_time`` of the period created by the :obj:`.period_future` recipe.
FUTURE_PERIOD_END = datetime(9999, 12, 31, 23, 59)

#: The ``first_deadline`` of the assignment created by the
#: :obj:`.assignment_futureperiod_start`.
ASSIGNMENT_FUTUREPERIOD_START_FIRST_DEADLINE = datetime(6000, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_futureperiod_end`.
ASSIGNMENT_FUTUREPERIOD_MIDDLE_PUBLISHING_TIME = datetime(7500, 1, 1, 0, 0)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_futureperiod_end`.
ASSIGNMENT_FUTUREPERIOD_MIDDLE_FIRST_DEADLINE = datetime(7500, 1, 15, 23, 59)

#: The ``publishing_time`` of the assignment created by the
#: :obj:`.assignment_futureperiod_end`.
ASSIGNMENT_FUTUREPERIOD_END_PUBLISHING_TIME = datetime(9999, 12, 1, 0, 0)


#: Use this Recipe to create a Period that has start time
#: set to ``1000-01-01 00:00`` and end time set to ``1999-12-31 23:59:59``.
#:
#: This makes it possible to test with exact datetime values instead
#: of writing tests that mocks the time.
#:
#: Example usage::
#:
#:    period = mommy.make_recipe('devilry.apps.core.period_old')
#:
#: See also :obj:`.period_active` and :obj:`.period_future`.
period_old = recipe.Recipe(
    Period,
    start_time=OLD_PERIOD_START,
    end_time=datetime(1999, 12, 31, 23, 59, 59)
)


#: Use this Recipe to create a Period that has start time
#: set to ``2000-01-01 00:00`` and end time set to ``5999-12-31 23:59:59``.
#:
#: This makes it possible to test with exact datetime values instead
#: of writing tests that mocks the time.
#:
#: Example usage::
#:
#:    period = mommy.make_recipe('devilry.apps.core.period_active')
#:
#:
#: See also :obj:`.period_old` and :obj:`.period_future`.
period_active = recipe.Recipe(
    Period,
    start_time=ACTIVE_PERIOD_START,
    end_time=ACTIVE_PERIOD_END
)

#: Use this Recipe to create a Period that has start time
#: set to ``6000-01-01 00:00`` and end time set to ``9999-12-31 23:59:59``.
#:
#: This makes it possible to test with exact datetime values instead
#: of writing tests that mocks the time.
#:
#: Example usage::
#:
#:    period = mommy.make_recipe('devilry.apps.core.period_future')
#:
#:
#: See also :obj:`.period_active` and :obj:`.period_old`.
period_future = recipe.Recipe(
    Period,
    start_time=FUTURE_PERIOD_START,
    end_time=FUTURE_PERIOD_END
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``1000-01-01 00:00`` and ``first_deadline`` set to
#: ``1000-01-15 23:59``.
#:
#: This means that it is right at the beginning for a period created
#: with the :obj:`.period_old` recipe.
#:
#: The period (parentnode) defaults to a period created with :obj:`.period_old`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_start')
#:
#:
#: See also :obj:`.assignment_oldperiod_middle` :obj:`.assignment_oldperiod_end`
assignment_oldperiod_start = recipe.Recipe(
    Assignment,
    publishing_time=OLD_PERIOD_START,
    first_deadline=ASSIGNMENT_OLDPERIOD_START_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_old)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``1500-01-01 00:00`` and ``first_deadline`` set to
#: ``1500-01-15 23:59``.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_old`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_middle')
#:
#:
#: See also :obj:`.assignment_oldperiod_start` :obj:`.assignment_oldperiod_end`
assignment_oldperiod_middle = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_OLDPERIOD_MIDDLE_PUBLISHING_TIME,
    first_deadline=ASSIGNMENT_OLDPERIOD_MIDDLE_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_old)
)

#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``1999-12-01 00:00`` and ``first_deadline`` set to
#: ``1999-12-31 23:59``.
#:
#: This means that the first deadline is exactly at the end of
#: a period created with the :obj:`.period_old` recipe.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_old`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end')
#:
#:
#: See also :obj:`.assignment_oldperiod_start` :obj:`.assignment_oldperiod_middle`
assignment_oldperiod_end = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_OLDPERIOD_END_PUBLISHING_TIME,
    first_deadline=OLD_PERIOD_END,
    parentnode=recipe.foreign_key(period_old)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``2000-01-01 00:00`` and ``first_deadline`` set to
#: ``2000-01-15 23:59``.
#:
#: This means that it is right at the beginning for a period created
#: with the :obj:`.period_active` recipe.
#:
#: The period (parentnode) defaults to a period created with :obj:`.period_active`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
#:
#:
#: See also :obj:`.assignment_activeperiod_middle` :obj:`.assignment_activeperiod_end`
assignment_activeperiod_start = recipe.Recipe(
    Assignment,
    publishing_time=ACTIVE_PERIOD_START,
    first_deadline=ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_active)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``3500-01-01 00:00`` and ``first_deadline`` set to
#: ``3500-01-15 23:59``.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_active`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle')
#:
#:
#: See also :obj:`.assignment_activeperiod_start` :obj:`.assignment_activeperiod_end`
assignment_activeperiod_middle = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_ACTIVEPERIOD_MIDDLE_PUBLISHING_TIME,
    first_deadline=ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_active)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``5999-12-01 00:00`` and ``first_deadline`` set to
#: ``5999-12-31 23:59``.
#:
#: This means that the first deadline is exactly at the end of
#: a period created with the :obj:`.period_active` recipe.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_active`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end')
#:
#:
#: See also :obj:`.assignment_activeperiod_start` :obj:`.assignment_activeperiod_middle`
assignment_activeperiod_end = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_ACTIVEPERIOD_END_PUBLISHING_TIME,
    first_deadline=ACTIVE_PERIOD_END,
    parentnode=recipe.foreign_key(period_active)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``6000-01-01 00:00`` and ``first_deadline`` set to
#: ``6000-01-15 23:59``.
#:
#: This means that it is right at the beginning for a period created
#: with the :obj:`.period_future` recipe.
#:
#: The period (parentnode) defaults to a period created with :obj:`.period_future`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start')
#:
#:
#: See also :obj:`.assignment_futureperiod_middle` :obj:`.assignment_futureperiod_end`
assignment_futureperiod_start = recipe.Recipe(
    Assignment,
    publishing_time=FUTURE_PERIOD_START,
    first_deadline=ASSIGNMENT_FUTUREPERIOD_START_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_future)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``7500-01-01 00:00`` and ``first_deadline`` set to
#: ``7500-01-15 23:59``.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_future`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_middle')
#:
#:
#: See also :obj:`.assignment_futureperiod_start` :obj:`.assignment_futureperiod_end`
assignment_futureperiod_middle = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_FUTUREPERIOD_MIDDLE_PUBLISHING_TIME,
    first_deadline=ASSIGNMENT_FUTUREPERIOD_MIDDLE_FIRST_DEADLINE,
    parentnode=recipe.foreign_key(period_future)
)


#: Use this Recipe to create an Assignment that has ``publishing_time``
#: set to ``9999-12-01 00:00`` and ``first_deadline`` set to
#: ``9999-12-31 23:59``.
#:
#: This means that the first deadline is exactly at the end of
#: a period created with the :obj:`.period_future` recipe.
#:
#: The period (parentnode) defaults to
#: a period created with :obj:`.period_future`.
#:
#: Example usage::
#:
#:    assignment = mommy.make_recipe('devilry.apps.core.assignment_futureperiod_end')
#:
#:
#: See also :obj:`.assignment_futureperiod_start` :obj:`.assignment_futureperiod_middle`
assignment_futureperiod_end = recipe.Recipe(
    Assignment,
    publishing_time=ASSIGNMENT_FUTUREPERIOD_END_PUBLISHING_TIME,
    first_deadline=FUTURE_PERIOD_END,
    parentnode=recipe.foreign_key(period_future)
)
