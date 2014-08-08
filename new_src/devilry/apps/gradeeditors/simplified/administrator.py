from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                FieldSpec, PermissionDenied)
from ..models import Config
import examiner



@simplified_modelapi
class SimplifiedConfig(SimplifiedModelApi):
    class Meta:
        model = Config
        resultfields = FieldSpec('gradeeditorid', 'assignment', 'config')
        searchfields = FieldSpec()
        methods = ('create', 'read', 'update')

    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.assignment.can_save(user):
            raise PermissionDenied()



@simplified_modelapi
class SimplifiedFeedbackDraft(examiner.SimplifiedFeedbackDraft):
    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.id == None:
            raise ValueError('We should not be able to update FeedbackDraft. If you see this exception, we have a BUG.')
        if not obj.delivery.deadline.assignment_group.can_save(user):
            raise PermissionDenied()
