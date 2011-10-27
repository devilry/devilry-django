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
class SimplifiedSubject(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Subject`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedSubjectMetaMixin):
        """ Defines what methods an Administrator can use on a Subject object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedSubjectMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given subject contains no periods
        """
        return obj.periods.all().count() == 0
