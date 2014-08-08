from devilry.simplified import simplified_modelapi, FieldSpec
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import SimplifiedCandidateMetaMixin

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedCandidate(CanSaveBase):
    related_fields = ['assignment_group', 'student']

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
