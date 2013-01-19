from haystack import indexes
from haystack import site
from devilry_search.base import BaseIndex
from .models import Node
from .models import Subject
from .models import Period
from .models import Assignment




class AdminsSearchIndex(BaseIndex):
    admins = indexes.MultiValueField(model_attr='get_all_admin_ids')


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