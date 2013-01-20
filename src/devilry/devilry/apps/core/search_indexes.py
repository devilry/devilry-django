from haystack import indexes
from haystack import site
from devilry_search.base import BaseIndex
from .models import Node
from .models import Subject
from .models import Period
from .models import Assignment
from .models import AssignmentGroup




class AdminsSearchIndex(BaseIndex):
    admin_ids = indexes.MultiValueField(model_attr='get_all_admin_ids')


class NodeIndex(AdminsSearchIndex):
    pass

site.register(Node, NodeIndex)


class SubjectIndex(AdminsSearchIndex):
    pass

site.register(Subject, SubjectIndex)


class PeriodIndex(AdminsSearchIndex):
    start_time = indexes.DateTimeField(model_attr='start_time')
    end_time = indexes.DateTimeField(model_attr='end_time')

site.register(Period, PeriodIndex)


class AssignmentIndex(AdminsSearchIndex):
    publishing_time = indexes.DateTimeField(model_attr='publishing_time')

site.register(Assignment, AssignmentIndex)


class AssignmentGroupIndex(AdminsSearchIndex):
    examiner_ids = indexes.MultiValueField()
    student_ids = indexes.MultiValueField()

    def prepare_examiner_ids(self, obj):
        return [examiner.user.id for examiner in obj.examiners.all()]

    def prepare_student_ids(self, obj):
        return [candidate.student.id for candidate in obj.candidates.all()]


site.register(AssignmentGroup, AssignmentGroupIndex)