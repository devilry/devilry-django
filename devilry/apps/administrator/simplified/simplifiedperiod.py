from devilry.simplified import (simplified_modelapi, FieldSpec)
from devilry.coreutils.simplified.metabases import SimplifiedPeriodMetaMixin

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedPeriod(HasAdminsMixin, CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Period`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedPeriodMetaMixin):
        """ Defines what methods an Administrator can use on a Period object using the Simplified API """
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec(admins=['admins__username']) + SimplifiedPeriodMetaMixin.resultfields

    @classmethod
    def is_empty(cls, obj):
        """
        Return ``True`` if the given period contains no assignments
        """
        return obj.assignments.all().count() == 0
