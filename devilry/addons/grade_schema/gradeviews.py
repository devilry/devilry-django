from django import forms
from django.utils.translation import ugettext as _
from devilry.addons.examiner import feedback_view
from models import SchemaGrade, Entry, SchemaGradeResult
from django.forms.models import inlineformset_factory
from django.forms.models import BaseModelFormSet


class Form(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols':50, 'rows':2}))
    points = forms.IntegerField()
    class Meta:
        model = Entry
        fields = ['points', 'text']

SchemaGradeResultFormSet = inlineformset_factory(SchemaGrade, Entry)
form_cls = SchemaGradeResultFormSet
model_cls = SchemaGrade

def view(request, delivery_obj):
    schemagrade = delivery_obj.assignment_group.parentnode.schemagrade
    print schemagrade.entry_set.all()


    feedback_form = feedback_view.parse_feedback_form(request, delivery_obj)
    feedback_obj = feedback_form.instance
    if feedback_obj.content_object:
        grade_obj = feedback_obj.content_object
    else:
        grade_obj = model_cls()

    if request.method == 'POST':
        grade_form = form_cls(request.POST, instance=grade_obj, prefix='grade')
    else:
        grade_form = form_cls(instance=grade_obj, prefix='grade')

    if request.method == 'POST':
        if feedback_form.is_valid() and grade_form.is_valid():
            grade_form.save()
            feedback_form.instance.content_object = grade_form.instance
            feedback_form.save()
            return feedback_view.redirect_after_successful_save(delivery_obj)

    return feedback_view.render_default_response(request, delivery_obj,
            feedback_form, grade_form)
