from devilry.simplified import FieldSpec, simplified_modelapi
from devilry.coreutils.simplified.metabases import SimplifiedAssignmentMetaMixin

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedAssignment(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Assignment`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedAssignmentMetaMixin):
        """ Defines what methods an Administrator can use on an Assignment object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedAssignmentMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given assignment contains no assignmentgroups.
        """
        return obj.assignmentgroups.all().count() == 0
