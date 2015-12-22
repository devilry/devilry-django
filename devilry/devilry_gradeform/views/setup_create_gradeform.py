from django import http
from django.views import generic
from django.shortcuts import get_object_or_404, render

from devilry.apps.core.models import assignment as core_assignment
from devilry.devilry_gradeform.views import grade_form

class CreateGradeForm(generic.TemplateView):
    """

    """
    template_name = 'devilry_gradeform/create.gradeform.django.html'

    def get(self, request, assignment_id):
        """

        :param assignment_id:
        :return:
        """
        assignment = get_object_or_404(core_assignment.Assignment, id=assignment_id)

        if not (assignment.is_admin(request.user) or
                request.user.is_superuser):
            return http.HttpResponseForbidden('Forbidden')

        create_setup = grade_form.AdvancedGradeForm.render_setup(
            grade_form.AdvancedGradeForm(),
            assignment)

        return render(request, self.template_name, {'create_setup': create_setup})