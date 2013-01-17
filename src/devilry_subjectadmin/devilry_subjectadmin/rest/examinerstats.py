from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from devilry_subjectadmin.rest.auth import IsAssignmentAdmin


class ExaminerStats(View):
    """
    Statistics for all examiners on an assignment.

    # GET

    ## Parameters
    Takes the assignment ID as the last item in the URL-path.

    ## Returns
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)

    def get(self, request, id=None):
        return []