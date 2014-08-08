from devilry.simplified import simplified_modelapi, FieldSpec, FilterSpec, FilterSpecs
from devilry.coreutils.simplified.metabases import SimplifiedExaminerMetaMixin
from devilry.apps.core.models import AssignmentGroupTag

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedAssignmentGroupTag(CanSaveBase):
    """ Simplified wrapper for :class:`devilry.apps.core.models.AssignmentGroupTag`. """
    class Meta(HasAdminsMixin.MetaMixin):
        """ Defines what methods an Administrator can use on an AssignmentGroupTag object using the Simplified API """
        model = AssignmentGroupTag
        methods = ('create', 'read', 'update', 'delete', 'search')
        editablefields = ('tag', 'assignment_group')
        resultfields = FieldSpec('id', 'assignment_group', 'tag')
        searchfields = FieldSpec()
        filters = FilterSpecs(FilterSpec('id'),
                              FilterSpec('tag'),
                              FilterSpec('assignment_group'),
                              FilterSpec('assignment_group__parentnode'), # Assignment
                              FilterSpec('assignment_group__parentnode__parentnode'), # Period
                              FilterSpec('assignment_group__parentnode__parentnode__parentnode') # Subject
                             )

    @classmethod
    def is_empty(cls, obj):
        return True
