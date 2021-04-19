from django.conf import settings
from model_bakery import baker


def examiner(group=None, shortname=None, fullname=None, automatic_anonymous_id=None):
    """
    Creates an Examiner using ``baker.make('core.Examiner', ...)``.

    Args:
        group: The AssignmentGroup to add the examiner to (optional).
        shortname: The ``shortname`` of the user (optional).
        fullname: The ``fullname`` of the user (optional).
        automatic_anonymous_id: The ``automatic_anonymous_id`` of the RelatedExaminer (optional).

    Returns:
        Examiner: The created examiner.
    """
    user_kwargs = {}
    if shortname:
        user_kwargs['shortname'] = shortname
    if fullname:
        user_kwargs['fullname'] = fullname

    relatedexaminer_kwargs = {}
    if automatic_anonymous_id:
        relatedexaminer_kwargs['automatic_anonymous_id'] = automatic_anonymous_id

    return baker.make(
        'core.Examiner',
        assignmentgroup=group,
        relatedexaminer=baker.make('core.RelatedExaminer',
                                   user=baker.make(settings.AUTH_USER_MODEL,
                                                   **user_kwargs),
                                   **relatedexaminer_kwargs)
    )


def candidate(group=None, shortname=None, fullname=None,
              automatic_anonymous_id=None, relatedstudents_candidate_id=None,
              candidates_candidate_id=None):
    """
    Creates a Candidate using ``baker.make('core.Candidate', ...)``.

    Args:
        group: The AssignmentGroup to add the candidate to (optional).
        shortname: The ``shortname`` of the user (optional).
        fullname: The ``fullname`` of the user (optional).
        automatic_anonymous_id: The ``automatic_anonymous_id`` of the RelatedStudent (optional).
        relatedstudents_candidate_id: The ``candidate_id`` of the RelatedStudent (optional).
        candidates_candidate_id: The ``candidate_id`` of the Candidate (optional).

    Returns:
        Candidate: The created candidate.
    """
    user_kwargs = {}
    if shortname:
        user_kwargs['shortname'] = shortname
    if fullname:
        user_kwargs['fullname'] = fullname

    relatedstudent_kwargs = {}
    if automatic_anonymous_id:
        relatedstudent_kwargs['automatic_anonymous_id'] = automatic_anonymous_id
    if relatedstudents_candidate_id:
        relatedstudent_kwargs['candidate_id'] = relatedstudents_candidate_id

    candidate_kwargs = {}
    if candidates_candidate_id:
        candidate_kwargs['candidate_id'] = candidates_candidate_id

    return baker.make(
        'core.Candidate',
        assignment_group=group,
        relatedstudent=baker.make('core.RelatedStudent',
                                  user=baker.make(settings.AUTH_USER_MODEL,
                                                  **user_kwargs),
                                  **relatedstudent_kwargs)
    )
