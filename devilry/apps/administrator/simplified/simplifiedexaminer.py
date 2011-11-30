from devilry.simplified import simplified_modelapi, FieldSpec, FilterSpec, FilterSpecs
from devilry.coreutils.simplified.metabases import SimplifiedExaminerMetaMixin

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedExaminer(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Examiner`. """
    class Meta(HasAdminsMixin.MetaMixin, SimplifiedExaminerMetaMixin):
        """ Defines what methods an Administrator can use on an Examiner object using the Simplified API """
        methods = ('create', 'read', 'update', 'delete', 'search')
        editablefields = ('user', 'assignmentgroup')
        resultfields = FieldSpec('user',
                                 userdetails=['user__username', 'user__email',
                                              'user__devilryuserprofile__full_name']) \
                + SimplifiedExaminerMetaMixin.resultfields
        filters = FilterSpecs(FilterSpec('user')) + SimplifiedExaminerMetaMixin.filters

    @classmethod
    def is_empty(cls, obj):
        return True
