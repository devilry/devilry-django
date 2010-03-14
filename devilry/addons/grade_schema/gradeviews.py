from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from django.utils.translation import ugettext as _
from devilry.addons.examiner import feedback_view
from models import SchemaGrade, Entry, Result, SchemaGradeResults
from django.forms.models import inlineformset_factory


class Form(forms.ModelForm):
    points = forms.IntegerField(widget=forms.TextInput(attrs={'size': 6}))
    class Meta:
        model = Result
        fields = ['points']
SchemaGradeResultFormSet = inlineformset_factory(SchemaGradeResults, Result,
        form=Form, extra=0, can_delete=False)

def view(request, delivery_obj):

    feedback_form = feedback_view.parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.content_object:
        schemagrade_results_obj = feedback_obj.content_object
    else:
        # Create the feedback and all initial results on first view.
        schemagrade_results_obj = SchemaGradeResults()
        schemagrade_results_obj.save()
        feedback_obj.content_object = schemagrade_results_obj
        feedback_obj.save()
        schemagrade = delivery_obj.assignment_group.parentnode.schemagrade
        for entry in schemagrade.entry_set.all():
            schemagrade_results_obj.result_set.add(Result(entry=entry, points=0))

    if request.method == 'POST':
        grade_form = SchemaGradeResultFormSet(request.POST, instance=schemagrade_results_obj, prefix='grade')
    else:
        grade_form = SchemaGradeResultFormSet(instance=schemagrade_results_obj, prefix='grade')

    entry_text = [r.entry.text for r in schemagrade_results_obj.result_set.all()]

    if request.method == 'POST':
        if feedback_form.is_valid() and grade_form.is_valid():
            grade_form.save()
            feedback_form.instance.content_object = grade_form.instance
            feedback_form.save()
            return feedback_view.redirect_after_successful_save(delivery_obj)

    return render_to_response('devilry/grade_schema/feedback.django.html', {
            'delivery': delivery_obj,
            'feedback_form': feedback_form,
            'grade_form': grade_form,
            'forms': zip(entry_text, grade_form.forms),
        }, context_instance=RequestContext(request))
