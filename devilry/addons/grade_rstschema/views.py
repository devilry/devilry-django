from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _

from devilry.ui.messages import UiMessages
from devilry.core.models import Assignment

from models import RstSchemaDefinition
from parser import RstValidationError, rstdoc_from_string


class RstSchemaDefinitionForm(forms.ModelForm):
    class Meta:
        model = RstSchemaDefinition
        fields = ('schemadef', 'let_students_see_schema')
        widgets = {
            'schemadef': forms.Textarea(attrs={'rows':40, 'cols':70})
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            rstdoc_from_string(cleaned_data['schemadef'])
        except RstValidationError, e:
            msg = _('Line %(line)s: %(message)s') % e.__dict__
            self._errors['schemadef'] = self.error_class([msg])
            del cleaned_data['schemadef']
        return cleaned_data



@login_required
def edit_schema(request, assignment_id, save_successful=False):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not assignment.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    messages = UiMessages()
    if save_successful:
        messages.add_success(_('Save successful'))

    try:
        schema = RstSchemaDefinition.objects.get(assignment=assignment_id)
    except RstSchemaDefinition.DoesNotExist, e:
        schema = RstSchemaDefinition(assignment=assignment)

    if request.method == 'POST':
        form = RstSchemaDefinitionForm(request.POST, instance=schema)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                    reverse('devilry-grade_rstschema-edit_schema-success',
                        args=[str(assignment_id)]))
    else:
        form = RstSchemaDefinitionForm(instance=schema)

    return render_to_response('devilry/grade_rstschema/edit.django.html', {
        'schema': schema,
        'messages': messages,
        'form': form,
        'assignment': assignment,
        }, context_instance=RequestContext(request))
