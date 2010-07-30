from django import forms
from devilry.addons.examiner.feedback_view import view_shortcut
from models import RstSchemaGrade, RstSchemaDefinition

class RstSchemaGradeForm(forms.ModelForm):
    class Meta:
        model = RstSchemaGrade
        fields = ('schema',)
        widgets = {
            'schema': forms.Textarea(attrs={'rows':40, 'cols':70})
        }


from django.shortcuts import render_to_response
from django.template import RequestContext
from devilry.addons.examiner.feedback_view import \
    render_response, parse_feedback_form, redirect_after_successful_save
import html
import text


def view(request, delivery_obj):
    feedback_form = parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.grade:
        grade_obj = feedback_obj.grade
    else:
        grade_obj = RstSchemaGrade()

    assignment = feedback_obj.get_assignment()
    schemadef = RstSchemaDefinition.objects.get(assignment=assignment)
    #print schemadef.schemadef

    #if request.method == 'POST':
        #grade_form = RstSchemaGradeForm(request.POST, instance=grade_obj, prefix='grade')
    #else:
        #grade_form = RstSchemaGradeForm(instance=grade_obj, prefix='grade')

    if request.method == 'POST':
        gradeform_errors, gradeform_values, grade_form = html.input_form(
                schemadef.schemadef, request.POST, validate=True)
        if feedback_form.is_valid() and not gradeform_errors:
            schema = text.examiner_format(schemadef.schemadef)
            schema = text.insert_values(schema, gradeform_values)
            grade_obj.schema = schema
            grade_obj.save()
            feedback_form.instance.grade = grade_obj
            feedback_form.save()
            return redirect_after_successful_save(delivery_obj)
    else:
        if grade_obj.schema:
            input_data = text.extract_valuedict(grade_obj.schema)
            print grade_obj.schema
            print input_data
        else:
            input_data = {}
        gradeform_errors, gradeform_values, grade_form = html.input_form(
                schemadef.schemadef, input_data)

    return render_to_response('devilry/grade_rstschema/feedback.django.html', {
            'delivery': delivery_obj,
            'feedback_form': feedback_form,
            'grade_form': grade_form,
        }, context_instance=RequestContext(request))
