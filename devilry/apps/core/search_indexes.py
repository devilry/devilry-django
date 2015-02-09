from haystack import indexes
from datetime import datetime

from devilry.devilry_search.base import BaseIndex

from devilry.apps.core import models


class AdminsSearchIndex(BaseIndex):
    admin_ids = indexes.MultiValueField(model_attr='get_all_admin_ids')

    #: The title of the item - typically a non-unique name for the item
    title = indexes.CharField()

    #: The unique path of the item - typically shown alongside the title
    path = indexes.CharField()

    def prepare_title(self, obj):
        return obj.long_name

    def prepare_path(self, obj):
        return obj.get_path()


class NodeIndex(AdminsSearchIndex, indexes.Indexable):
    def index_queryset(self, using=None):
        qry = super(NodeIndex, self).index_queryset()
        qry = qry.prefetch_related('admins')
        return qry

    def get_model(self):
        return models.Node


class SubjectIndex(AdminsSearchIndex, indexes.Indexable):
    def index_queryset(self, using=None):
        qry = super(SubjectIndex, self).index_queryset()
        qry = qry.prefetch_related('admins')
        return qry

    def get_model(self):
        return models.Subject


class PeriodIndex(AdminsSearchIndex, indexes.Indexable):
    start_time = indexes.DateTimeField(model_attr='start_time')
    end_time = indexes.DateTimeField(model_attr='end_time')

    def index_queryset(self, using=None):
        qry = super(PeriodIndex, self).index_queryset()
        qry = qry.select_related('parentnode')
        qry = qry.prefetch_related(
            'admins',
            'parentnode__admins')
        return qry

    def get_model(self):
        return models.Period


class AssignmentIndex(AdminsSearchIndex, indexes.Indexable):
    publishing_time = indexes.DateTimeField(model_attr='publishing_time')
    is_active = indexes.BooleanField(model_attr='is_active')
    examiner_ids = indexes.MultiValueField()

    def prepare_examiner_ids(self, obj):
        return [
            examiner.user.id
            for examiner in models.Examiner.objects.filter(assignmentgroup__parentnode=obj.id)]

    def index_queryset(self, using=None):
        qry = super(AssignmentIndex, self).index_queryset()
        qry = qry.select_related(
            'parentnode'
            'parentnode__parentnode')
        qry = qry.prefetch_related(
            'admins',
            'parentnode__admins',
            'parentnode__parentnode__admins')
        return qry

    def get_model(self):
        return models.Assignment


class AssignmentGroupIndex(AdminsSearchIndex, indexes.Indexable):
    examiner_ids = indexes.MultiValueField()
    student_ids = indexes.MultiValueField()
    examiners = indexes.CharField(use_template=True)
    candidates = indexes.CharField(use_template=True)
    tags = indexes.CharField(use_template=True)
    is_active = indexes.BooleanField()
    is_published = indexes.BooleanField()

    def prepare_examiner_ids(self, obj):
        return [examiner.user.id for examiner in obj.examiners.all()]

    def prepare_student_ids(self, obj):
        return [candidate.student.id for candidate in obj.candidates.all()]

    def index_queryset(self, using=None):
        qry = super(AssignmentGroupIndex, self).index_queryset()
        qry = qry.select_related(
            'parentnode',  'parentnode__parentnode',
            'parentnode__parentnode__parentnode')
        qry = qry.prefetch_related(
            'tags',
            'parentnode__admins',
            'parentnode__parentnode__admins',
            'parentnode__parentnode__parentnode__admins',
            'examiners', 'examiners__user', 'examiners__user__devilryuserprofile',
            'candidates', 'candidates__student', 'candidates__student__devilryuserprofile')
        return qry

    def prepare_is_active(self, obj):
        return obj.parentnode.is_active()

    def prepare_is_published(self, obj):
        return obj.parentnode.publishing_time < datetime.now()

    def prepare_title(self, obj):
        return obj.long_displayname

    def prepare_path(self, obj):
        return u'{}.{}'.format(obj.assignment.get_path(), obj.short_displayname)

    def get_model(self):
        return models.AssignmentGroup
