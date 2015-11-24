from django import template

from devilry.devilry_gradeform.views import grade_form


register = template.Library()

@register.simple_tag(name="devilry_gradeform_editable_advanced")
def devilry_gradeform_editable_advanced(assignment, feedbackset):
    """

    :param assignment:
    :param feedbackset:
    :return:
    """
    return grade_form.AdvancedGradeForm.render_editable(grade_form.AdvancedGradeForm(), assignment, feedbackset)