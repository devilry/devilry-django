#########################
Passed In Previous Period
#########################

.. _passed_in_previous_period:

The passed in previous utility
==============================

:class:`devilry.utils.passed_in_previous_period.PassedInPreviousPeriod` takes an :class:`core.Assignment` which
is the assignment in the current period we want to approve passed assignments in. And a :class:`core.Period` which
is the earliest period back in time we want to approve passed assignments for.

For instance if the assignment is assignment1 in period spring2017 and the period is spring2015,
a student Dewey Duck who passed the assignment(assignment1) in spring2015 and he's attending to the subject
in spring2017 then Dewey Duck is qualified to pass the assignment in the current period.
A student who passed the assignment in spring2016 will also be qualified, but not a student who passed in spring2014.

If a student have passed the assignment in multiple semesters back in time the latest passed assignment and
grading will always be taken in account.


How will the assignment be graded?
----------------------------------
The supported grading plugins is :obj:`core.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED` and
:obj:`Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS`.

:meth:`devilry.devilry_group.models.FeedbacksetPassedPreviousPeriod.convert_points`
If the grading configuration varies in previous semesters
the grading points will be converted into the current grading configuration on the assignment.
For instance if max points on the assignment is 10 and passing grade min points is 6 on a previous assignment,
a student who got 9 points will get 5 points when max points is 5 and passing grade min points is 3 on the current assignment.
Which means if a decimal number is returned by the grading converter it will always round up to give favor for the student.


.. _feedbackset_passed_previous_period:

The FeedbacksetPassedPreviousPeriod model
=========================================

:class:`devilry.devilry_group.models.FeedbacksetPassedPreviousPeriod`
When a student got approved to pass the assignment in the current period we'll save some metadata about
the previous assignment(names and grading configuration), period(names, start- and end datetime)
and feedback(grading points, published by, published datetime).
