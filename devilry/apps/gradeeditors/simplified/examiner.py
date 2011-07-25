from django.db.models import Q

from devilry.apps.core.models import Assignment
from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                FieldSpec, PermissionDenied, FilterSpecs,
                                FilterSpec)
from ..models import Config, FeedbackDraft


@simplified_modelapi
class SimplifiedConfig(SimplifiedModelApi):
    class Meta:
        model = Config
        resultfields = FieldSpec('id', 'gradeeditorid', 'assignment', 'config')
        searchfields = FieldSpec()
        methods = ('read',)

    @classmethod
    def read_authorize(cls, user, obj):
        try:
            Assignment.objects.get(Assignment.q_is_examiner(user) & Q(id=obj.id))
        except Assignment.DoesNotExist:
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedFeedbackDraft(SimplifiedModelApi):
    class Meta:
        model = FeedbackDraft
        resultfields = FieldSpec('id', 'delivery', 'saved_by', 'save_timestamp', 'draft')
        searchfields = FieldSpec()
        filters = FilterSpecs(FilterSpec('delivery'))
        methods = ('create', 'read', 'search')
        editablefields = ('delivery', 'draft')

    @classmethod
    def create_searchqryset(self, user):
        return self._meta.model.objects.filter(saved_by=user)

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.saved_by == user:
            raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.delivery.deadline.assignment_group.is_examiner(user):
            raise PermissionDenied()

    @classmethod
    def pre_full_clean(cls, user, obj):
        obj.saved_by = user
