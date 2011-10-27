from django.contrib.auth.models import User
from django.db.models import Count, Max

from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied, InvalidUsername, FieldSpec,
                                FilterSpecs, FilterSpec, PatternFilterSpec,
                                stringOrNoneConverter, boolConverter)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin,
                                                   SimplifiedCandidateMetaMixin)
from devilry.apps.examiner.simplified import SimplifiedDelivery as ExaminerSimplifiedDelivery

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedCandidate(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedCandidateMetaMixin):
        """ Defines what methods an Administrator can use on an Assignment object using the Simplified API """
        methods = ('create', 'read', 'update', 'delete', 'search')
        editablefields = ('student', 'candidate_id', 'assignment_group')
        resultfields = FieldSpec('student', 'candidate_id') + SimplifiedCandidateMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignment contains no assignmentgroups.
        """
        return models.Delivery.objects.filter(deadline__assignment_group=obj.assignment_group, delivered_by=obj).count() == 0
