from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group.models import FeedbackSet


def feedbackset_first_try_published(grading_published_datetime=None, **kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    grading_published_datetime = grading_published_datetime or timezone.now()
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                      grading_published_datetime=grading_published_datetime,
                      **kwargs)


def feedbackset_new_try_published(grading_published_datetime=None, **kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    grading_published_datetime = grading_published_datetime or timezone.now()
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                      grading_published_datetime=grading_published_datetime,
                      **kwargs)


def feedbackset_first_try_unpublished(**kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                      **kwargs)


def feedbackset_new_try_unpublished(**kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    return mommy.make('devilry_group.FeedbackSet',
                      feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_TRY,
                      **kwargs)
