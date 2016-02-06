from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group.models import FeedbackSet


def feedbackset_first_attempt_published(grading_published_datetime=None, grading_points=1,
                                    **kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        grading_points: The ``grading_points`` of the feedbackset.
            Defaults to ``1``.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    grading_published_datetime = grading_published_datetime or timezone.now()
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                      grading_published_datetime=grading_published_datetime,
                      grading_points=grading_points,
                      **kwargs)


def feedbackset_new_attempt_published(grading_published_datetime=None, grading_points=1, **kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        grading_points: The ``grading_points`` of the feedbackset.
            Defaults to ``1``.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    grading_published_datetime = grading_published_datetime or timezone.now()
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                      grading_published_datetime=grading_published_datetime,
                      grading_points=grading_points,
                      **kwargs)


def feedbackset_first_attempt_unpublished(**kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                      **kwargs)


def feedbackset_new_attempt_unpublished(**kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                      **kwargs)
