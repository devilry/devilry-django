.. _utils_groups_groupedby_relatedstudent_and_assignment:

===================================================================
:mod:`devilry.utils.groups_groupedby_relatedstudent_and_assignment`
===================================================================

Provides an easy-to-use API for generating overviews over the results of all students in a period.
Collects students that are not related as well as related.

Example
=======

Create CSV with the grades of all students on the period, including those ignored because they
are not related::

    grouper = GroupsGroupedByRelatedStudentAndAssignment(myperiod)

    header = ['USER','IGNORED']
    for assignment in grouper.iter_assignments():
        header.append(assignment.short_name)
    print ';'.join(header)

    def print_aggregated_relstudentinfo(aggregated_relstudentinfo, ignored):
        user = aggregated_relstudentinfo.user
        row = [user.username, ignored]
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            # NOTE: There can be more than one group if the same student is in more than one
            #       group on an assignment - we select the "best" feedback.
            feedback = grouplist.get_feedback_with_most_points()
            if feedback:
                row.append(feedback.grade)
            else:
                row.append('NO-FEEDBACK')
        print ';'.join(row)

    # Print all related students
    for aggregated_relstudentinfo in grouper.iter_relatedstudents_with_results():
        print_aggregated_relstudentinfo(aggregated_relstudentinfo, 'NO')

    # Last we print the ignored students (non-related students that are in a group)
    for aggregated_relstudentinfo in grouper.iter_students_with_feedback_that_is_candidate_but_not_in_related():
        print_aggregated_relstudentinfo(aggregated_relstudentinfo, 'YES')


API
=======================

.. automodule:: devilry.utils.groups_groupedby_relatedstudent_and_assignment