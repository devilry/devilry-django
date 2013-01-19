import datetime
from haystack import indexes
from haystack import site
from devilry_search.base import BaseIndex
from .models import Assignment


class AssignmentIndex(BaseIndex):
    publishing_time = indexes.DateTimeField(model_attr='publishing_time')

site.register(Assignment, AssignmentIndex)