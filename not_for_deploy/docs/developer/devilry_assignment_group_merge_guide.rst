#################################################################################
:mod:`devilry.apps.core.AssignmentGroupHistory --- Assignment Group Merge history
:mod:`devilry.apps.core.AssignmentGroup --- Assignment Group
#################################################################################

.. _assignmentgroup_merge:

**********************************
How do we merge assignment groups?
**********************************

:meth:`core.AssignmentGroup.merge_groups` takes a list of :class:`core.AssignmentGroup`
where the first element will be target. The rest of the groups in the list will
be merged into target.

Merge Algorithm:
- Move all candidates from a :class:`core.AssignmentGroup` which is not present in target :class:`core.AssignmentGroup`
- Move all examiners from a :class:`core.AssignmentGroup` which is not present in target :class:`core.AssignmentGroup`
- Move all tags from a :class:`core.AssignmentGroup` which is not present in target :class:`core.AssignmentGroup`
- Move all :class:`devilry_group.FeedbackSet` into target :class:`core.AssignmentGroup` and change
    :obj:`devilry_group.FeedbackSet.feedbackset_type` to a merge prefex.
    For instance a :class:`devilry_group.Feedbackset` which has feedbackset_type FEEDBACKSET_TYPE_NEW_ATTEMPT
    will be changed to FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT. For FEEDBACKSET_TYPE_FIRST_ATTEMPT we have to also add
    the current deadline to the FeedbackSet.

To keep an audit trail of merges we have implemented an assignment group history.
The :class:`core.AssignmentGroupHistory` contains a json field which describes all the merges made for
a :class:`core.AssignmentGroup` in a B-tree structure. Before merging all the current states of the
assignment groups in the list will be dumped into json. Our current implementation gives the advantage of
a quite shallow state dump, since the only thing that will be removed is assignment groups. Feedbacksets will still
be present.

Other solutions we considered:
- Instead of only merge assignment groups in a shallow manner we also tried to merge feedbacksets pairwise ordered by
    deadline datetime. Then it is necessary to merge all comments within the feedbacksets
    which would give an incomprehensible timeline, imagine two chat logs merge into each other.
- We worked further with another approach where we only merged those feedbacksets which had the same deadline and grading points.
    But still we had the same problem with an incomprehensible timeline. Another problem that occurred was what if
    two assignment groups did not have equal amount of feedbacksets? This was also the case in the previous approach.
    To fix this we introduced a new feedbackset_type(merge-leftover), this led us to our current implementation which is
    much more simpler than these.

Both of the solutions above required a full state dump of feedbacksets to keep history.
