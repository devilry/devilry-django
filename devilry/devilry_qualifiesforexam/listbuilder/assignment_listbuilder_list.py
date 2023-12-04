
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.crinstance import reverse_cradmin_url

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.apps.core import models as coremodels

    
class AssignmentItemValue(listbuilder.base.ItemValueRenderer):
    valuealias = 'assignment'
    def get_extra_css_classes_list(self):
        css_classes_list = super().get_extra_css_classes_list()
        css_classes_list.append('devilry-cradmin-perioditemvalue-admin')
        return css_classes_list
    
    
class AssignmentItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'assignment'
    
    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='overview',
            roleid=self.assignment.id
        )
        
    def get_extra_css_classes_list(self):
        css_classes_list = super().get_extra_css_classes_list()
        
        css_classes_list.append('cradmin-legacy-listbuilder-itemvalue'
                                ' cradmin-legacy-listbuilder-itemvalue-focusbox'
                                ' cradmin-legacy-listbuilder-itemvalue-titledescription'
                                ' devilry-frontpage-listbuilder-roleselect-itemvalue'
                                ' devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin')
        
        return css_classes_list
    
    

class AssignmentListBuilderList(listbuilder.base.List):
    def append_assignment(self, assignment_id):
        assignment = coremodels.Assignment.objects.get(id=assignment_id)
        item_value = AssignmentItemValue(value=assignment)
        valuerenderer = AssignmentItemFrame(inneritem=item_value, roleid=assignment_id)
        self.append(renderable=valuerenderer)
        
    @classmethod
    def from_assignment_id_list(cls, assignment_id_list):
        assignment_list = cls()
        for assignment_id in assignment_id_list:
            assignment_list.append_assignment(assignment_id)
        return assignment_list