from django import forms

from devilry.addons.examiner.feedback_view import \
    parse_feedback_form, redirect_after_successful_save, render_response, \
    save_feedback_form

from models import RstSchemaGrade, RstSchemaDefinition
import html
import text



class RstSchemaGradeForm(forms.ModelForm):
    class Meta:
        model = RstSchemaGrade
        fields = ('schema',)
        widgets = {
            'schema': forms.Textarea(attrs={'rows':40, 'cols':70})
        }


def view(request, delivery_obj):
    feedback_form = parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.grade:
        grade_obj = feedback_obj.get_grade()
        first_save = False
    else:
        grade_obj = RstSchemaGrade()
        first_save = True

    assignment = feedback_obj.get_assignment()
    schemadef = RstSchemaDefinition.objects.get(assignment=assignment)

    if request.method == 'POST':
        gradeform_errors, gradeform_values, grade_form = html.input_form(
                schemadef.schemadef, request.POST, validate=True)
        if feedback_form.is_valid() and not gradeform_errors:
            schema = text.examiner_format(schemadef.schemadef)
            schema = text.insert_values(schema, gradeform_values)
            grade_obj.schema = schema
            grade_obj.save(feedback_form.instance)
            feedback_form.instance.grade = grade_obj
            save_feedback_form(request, feedback_form)
            return redirect_after_successful_save(request, delivery_obj)
    else:
        if grade_obj.schema:
            input_data = text.extract_valuedict(grade_obj.schema)
        else:
            input_data = {}
        gradeform_errors, gradeform_values, grade_form = html.input_form(
                schemadef.schemadef, input_data)

    return render_response(request, delivery_obj, feedback_form, grade_form,
            'devilry/grade_rstschema/feedback.django.html')
