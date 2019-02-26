# -*- coding: utf-8 -*-


from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy

from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_dbcache import models as cache_models


def feedbackset_save(feedbackset, **kwargs):
    """
    Set attributes for a FeedbackSet-instance and save it.

    Args:
        feedbackset: FeedbackSet to save.
    """
    for key, value in kwargs.items():
        setattr(feedbackset, key, value)
    feedbackset.save()


def _make_assignment_group_for_feedbackset(group, **kwargs):
    groupkwargs = {}
    for key in list(kwargs.keys()):
        if key.startswith('group__'):
            value = kwargs.pop(key)
            groupkey = key[len('group__'):]
            groupkwargs[groupkey] = value
    if group:
        if groupkwargs:
            raise ValueError('You can not supply a group AND supply kwargs starting '
                             'with group__.')
    else:
        group = mommy.make('core.AssignmentGroup', **groupkwargs)
    return group


def make_first_feedbackset_in_group(group=None, **feedbackset_attributes):
    """
    Get the first feedbackset in a group, and optionally update some attributes.

    This is designed to be used instead of ``mommy.make('devilry_group.FeedbackSet')``
    when you just want a FeedbackSet since that does not work because the
    postgres triggers automatically create the first feedbackset in each
    created AssignmentGroup.

    Examples:

        Create a FeedbackSet::

            feedbackset = devilry_group_mommy_factories.make_first_feedbackset_in_group()

        With attributes::

            feedbackset = devilry_group_mommy_factories.make_first_feedbackset_in_group(
                ignored_reason='Test')

        With pre-existing AssignmentGroup::

            group = mommy.make('core.AssignmentGroup')
            feedbackset = devilry_group_mommy_factories.make_first_feedbackset_in_group(
                group=group)

        Create AssignmentGroup with attributes::

            group = mommy.make('core.AssignmentGroup')
            feedbackset = devilry_group_mommy_factories.make_first_feedbackset_in_group(
                group__parentnode__short_name='assignment1',
                group__parentnode__parentnode__short_name='period1')

    Args:
        group (devilry.apps.core.models.assignment_group.AssignmentGroup): An AssignmentGroup.
            If this is ``None``, the group is created using mommy.make(),
            and all the attributes in ``feedbackset_attributes`` starting
            with ``group__``.
        **feedbackset_attributes: Optional attributes for the feedbackset.
            If provided, the feedbackset is updated with these attributes
            (and saved to the database). Does not clean before saving.

    Returns:
        devilry.devilry_group.models.FeedbackSet: The retrieved
            (and updated if feedbackset_attributes is provided) FeedbackSet.
    """
    group = _make_assignment_group_for_feedbackset(group=group, **feedbackset_attributes)
    first_feedbackset = group.feedbackset_set.first()
    if feedbackset_attributes:
        for key, value in list(feedbackset_attributes.items()):
            setattr(first_feedbackset, key, value)
        first_feedbackset.save()
    return first_feedbackset


def feedbackset_first_attempt_published(group=None, grading_published_datetime=None, grading_points=1, **kwargs):
    """
    Updates the autogenerated FeedbackSet.

    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Note::
        If no group is passed as parameter(param group is None), an AssignmentGroup will be created which triggers an
        automatic creation of a FeedbackSet. This is the FeedbackSet that is returned.
        An examiner is also autogenerated for FeedbackSet.grading_published_by.

    Args:
        group: AssignmentGroup for the first FeedbackSet.
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        grading_points: The ``grading_points`` of the feedbackset.
            Defaults to ``1``.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: Instance of the first FeedbackSet.
    """
    group = _make_assignment_group_for_feedbackset(group=group, **kwargs)
    group_cache = cache_models.AssignmentGroupCachedData.objects.get(group=group)
    first_feedbackset = group_cache.first_feedbackset
    first_feedbackset.feedbackset_type = FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT
    first_feedbackset.grading_published_datetime = grading_published_datetime or timezone.now()
    first_feedbackset.grading_points = grading_points
    examiner = mommy.make('core.Examiner', assignmentgroup=group)
    first_feedbackset.grading_published_by = examiner.relatedexaminer.user
    feedbackset_save(feedbackset=first_feedbackset, **kwargs)
    return first_feedbackset


def feedbackset_first_attempt_unpublished(group=None, **kwargs):
    """
    Creates a unpublished FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Note::
        If no group is passed as parameter(param group is None), an AssignmentGroup will be created which triggers an
        automatic creation of a FeedbackSet. This is the FeedbackSet that is returned.

    Args:
        group: AssignmentGroup for the first FeedbackSet.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: Instance of the first FeedbackSet.
    """
    group = _make_assignment_group_for_feedbackset(group=group, **kwargs)
    group_cache = cache_models.AssignmentGroupCachedData.objects.get(group=group)
    first_feedbackset = group_cache.first_feedbackset
    first_feedbackset.feedbackset_type = FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT
    feedbackset_save(first_feedbackset, **kwargs)
    return first_feedbackset


def feedbackset_new_attempt_published(group, grading_published_datetime=None, grading_points=1, **kwargs):
    """
    Creates a published FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        group: The AssignmentGroup the FeedbackSet should belong to.
        grading_published_datetime: The ``grading_published_datetime`` of the feedbackset.
            Defaults to ``timezone.now()`` if not specified.
        grading_points: The ``grading_points`` of the feedbackset.
            Defaults to ``1``.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    if not group:
        raise ValueError('A FeedbackSet as a new attempt must have a pre-existing group!')
    kwargs.setdefault('deadline_datetime', timezone.now())
    if 'grading_published_by' not in kwargs:
        examiner = mommy.make('core.Examiner', assignmentgroup=group)
        kwargs['grading_published_by'] = examiner.relatedexaminer.user
    feedbackset = mommy.prepare(
        'devilry_group.FeedbackSet',
        group=group,
        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
        grading_published_datetime=grading_published_datetime or timezone.now(),
        grading_points=grading_points,
        **kwargs
    )
    feedbackset.full_clean()
    feedbackset.save()
    return feedbackset


def feedbackset_new_attempt_unpublished(group, **kwargs):
    """
    Creates a unpublished FeedbackSet with ``feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT``
    using ``mommy.make('devilry_group.FeedbackSet)``.

    Args:
        group: The AssignmentGroup the FeedbackSet should belong to.
        kwargs: Other attributes for FeedbackSet.

    Returns:
        FeedbackSet: The created FeedbackSet.
    """
    if not group:
        raise ValueError('A FeedbackSet as a new attempt must have a pre-existing group!')
    kwargs.setdefault('deadline_datetime', timezone.now() + timezone.timedelta(days=3))
    feedbackset = mommy.prepare(
        'devilry_group.FeedbackSet',
        group=group,
        feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
        **kwargs)
    feedbackset.full_clean()
    feedbackset.save()
    return feedbackset


def _add_file_to_collection(temporary_filecollection, file_like_object):
    """
    Creates a :obj:`django_cradmin.apps.cradmin_temporaryfileuploadstore.models.TemporaryFile` for the
    ``temporary_filecollection```.

    Args:
        temporary_filecollection: TemporaryFileCollection for the TemporaryFile created.
        file_like_object: A object that implements the general file attributes.
    """
    mommy.make('cradmin_temporaryfileuploadstore.TemporaryFile',
               collection=temporary_filecollection,
               filename=file_like_object.name,
               file=file_like_object,
               mimetype=file_like_object.content_type)


def temporary_file_collection_with_tempfile(**collection_attributes):
    """
    Create a :obj:`django_cradmin.apps.cradmin_temporaryfileuploadstore.models.TemporaryFileCollection`
    using ``mommy.make('cradmin_temporaryfileuploadstore.TemporaryFileCollection')`` with a attached default
    :obj:`django_cradmin.apps.cradmin_temporaryfileuploadstore.models.TemporaryFile`.

    Note::
        Use this if you don't care for the actual file, only that a file is added.

    Args:
        **temporary_filecollection_attributes: Attributes for TemporaryFileCollection.

    Returns:
        cradmin_temporaryfileuploadstore.TemporaryFileCollection: TemporaryFileCollection instance.
    """
    temp_collection = mommy.make('cradmin_temporaryfileuploadstore.TemporaryFileCollection', **collection_attributes)
    _add_file_to_collection(
        temporary_filecollection=temp_collection,
        file_like_object=SimpleUploadedFile(name='testfile.txt', content=b'Test content', content_type='text/txt')
    )
    return temp_collection


def temporary_file_collection_with_tempfiles(file_list=None, **collection_attributes):
    """
    Create a :obj:`django_cradmin.apps.cradmin_temporaryfileuploadstore.models.TemporaryFileCollection`
    using ``mommy.make('cradmin_temporaryfileuploadstore.TemporaryFileCollection')``.

    Add files to the ``file_list``, preferably Django`s ``SimpleUploadedFile``.

    Examples:

        Create a TemporaryFileCollection with TemporaryFiles (adds 3 files)::

            devilry_group_mommy_factories.temporary_file_collection_with_tempfiles(
                file_list=[
                    SimpleUploadedFile(name='testfile1.txt', content=b'Test content 1', content_type='text/txt'),
                    SimpleUploadedFile(name='testfile1.txt', content=b'Test content 1', content_type='text/txt'),
                    SimpleUploadedFile(name='testfile1.txt', content=b'Test content 1', content_type='text/txt')
                ],
                # attributes for the TemporaryFileCollection
                ...
            )

    Args:
        file_list: A list of files implementing the general attributes of a file.
        **collection_attributes: Attributes for TemporaryFileCollection.

    Returns:
        cradmin_temporaryfileuploadstore.TemporaryFileCollection: TemporaryFileCollection.
    """
    temp_collection = mommy.make('cradmin_temporaryfileuploadstore.TemporaryFileCollection', **collection_attributes)
    if file_list:
        for file_obj in file_list:
            _add_file_to_collection(temporary_filecollection=temp_collection, file_like_object=file_obj)
    return temp_collection
