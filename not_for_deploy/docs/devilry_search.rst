==========================================================
:mod:`devilry_search` --- Search for Devilry
==========================================================
This app provides a search API for Devilry.




How we handle object level permissions
######################################
We maintain a list of ``admin_ids`` on Node, Subject, Period, Assignment and AssignmentGroup. On
AssignmentGroup, we also maintain a list of ``examiner_ids`` and ``student_ids``. When we perform
a search, we filter on these ids (the requesting user must be in an id-list). I.E:

    When we search for assignments, we first filter on ``admin_ids=request.user.id``, then we
    perform the search.


Protection of anonymous data
############################
We do not include any sensitive data in the main search index:

- No student names on anonymous assignments --- Examiners should not be able to search for these
  because they are only supposed to know the candidate ID.
- No examiner names on anonymous assignments --- Students should not be able to know who their
  examiner is.
- Tags --- Only examiners and admins are supposted to see tags.

This is handled in the ``devilry.apps.core.search_indexes.AssignmentGroupIndex``, and the exclusions
is handled by the text-template in the ``search/indexes/core/assignmentgroup_text.txt`` template
(located in ``devilry/apps/core/templates/``).

We include the excluded data in their own fields in ``AssignmentGroupIndexes``.
The fields, ``examiners``, ``tags`` and ``candidates``, may be used to search for
the excluded terms.


Limitations
###########

We do not currently use the excluded fields mentioned in the previous section in the search API.
This means that it is:

- not possible to search for AssignmentGroups by username or examiner on anonymous assignments.
- not possible to search for AssignmentGroups by tags.