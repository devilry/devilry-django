from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _
from ..ui.messages import UiMessages
from models import SchemaGrade, Entry
from ..core.models import Assignment


class EntryForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols':50, 'rows':2}))
    max_points = forms.IntegerField()
    class Meta:
        model = Entry
        fields = ['max_points', 'text']
SchemaFormSet = inlineformset_factory(SchemaGrade, Entry, form=EntryForm)


@login_required
def edit_schema(request, assignment_id, messages=None):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    try:
        schema = SchemaGrade.objects.get(assignment=assignment_id)
    except SchemaGrade.DoesNotExist, e:
        schema = SchemaGrade(assignment=assignment)
        schema.save()

    if request.method == 'POST':
        formset = SchemaFormSet(request.POST, instance=schema)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(
                    reverse(__name__ + '.successful_save',
                        args=[str(assignment_id)]))
    else:
        formset = SchemaFormSet(instance=schema)

    return render_to_response('devilry/grade_schema/edit.django.html', {
        'schema': schema,
        'messages': messages,
        'formset': formset,
        'assignment': assignment,
        }, context_instance=RequestContext(request))


@login_required
def successful_save(request, assignment_id):
    messages = UiMessages()
    messages.add_success(_('Save successful'))
    return edit_schema(request, assignment_id, messages)
