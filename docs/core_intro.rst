################################
Introduction to the Devilry core
################################

.. currentmodule:: devilry.apps.core.models

.. note:: This is incomplete.


The Devilry core is simply a collection of Django data models.
To ensure that all common operations are fast, we have a higher
level API for creating, updating and removing some of the core
data models. We also have a few cached fields to work around
restrictions in relational databases without resorting to database
specific queries.


.. _core_createupdateremove:

********************************************
Creating, updating and removing core objects
********************************************

Candidate
=========
To add and remove :class:`candidates <.Candidate>`, use:

- :meth:`~.CandidateManager.bulkadd_candidates_to_groups`.
..   - :meth:`~.CandidateManager.bulkremove_candidates_from_groups`.


Examiner
========
To add and remove :class:`examiners <.Examiner>`, use the methods in :class:`~.ExaminerManager`


Creating AssignmentGroups
=========================
An :class:`.AssignmentGroup` (groups) is just an empty shell until you add candidates. This means that it rarely makes sense to create groups without also adding candidates. Example::

    created_groups = AssignmentGroup.objects.create_x_groups(myassignment, 2)
    Candidate.objects.bulkadd_candidates_to_groups(
        groups=created_groups,
        grouped_candidates=[
            [Candidate(student=user1), Candidate(student=user1)],
            [Candidate(student=user3)]
        ]
    )



*************
Cached fields
*************
The Devilry core has a few cached fields to work around
restrictions in relational databases without resorting to database
specific queries.

Make sure  you use the APIs described in :ref:`.core_createupdateremove` to
ensure these fields are handled correctly.


Candidate
=========
- :obj:`~devilry.apps.core.models.Candidate.only_candidate_in_group`

Deprecated fields (will soon be removed, and should NOT be used for new code):

- :obj:`~.Candidate.identifier`
- :obj:`~.Candidate.full_name`
- :obj:`~.Candidate.email`
