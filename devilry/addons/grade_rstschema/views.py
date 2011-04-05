from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
        HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _
from django.conf import settings

from devilry.ui.messages import UiMessages
from devilry.core.models import Assignment, Subject, Period, AssignmentGroup
from devilry.core.utils.GroupNodes import group_assignmentgroups

from html import input_form
from models import RstSchemaDefinition
from parser import RstValidationError, rstdoc_from_string




class RstSchemaDefWidget(forms.Textarea):
    class Media:
        js = (
            settings.DEVILRY_RESOURCES_URL + "/markitup/markitup/jquery.markitup.js",
            settings.DEVILRY_RESOURCES_URL + "/markitup/markitup/sets/rst/rstschemadef.js",
            settings.DEVILRY_RESOURCES_URL + "/ui/js/rstedit_widget.js",
        )
        css = {
            'all': [
                settings.DEVILRY_RESOURCES_URL + "/markitup/markitup/skins/simple/style.css",
                settings.DEVILRY_RESOURCES_URL + "/markitup/markitup/sets/rst/style.css"
        ]}

    def __init__(self, attrs={}):
        if not 'cols' in attrs:
            attrs["cols"] = 70
        if not 'rows' in attrs:
            attrs["rows"] = 35
        attrs["class"] = "devilry_rstedit"
        super(RstSchemaDefWidget, self).__init__(attrs)


class RstSchemaDefinitionForm(forms.ModelForm):
    class Meta:
        model = RstSchemaDefinition
        fields = ('schemadef', 'let_students_see_schema', 'maxpoints', 'grade_to_points_mapping')
        widgets = {
            'schemadef': RstSchemaDefWidget
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            rstdoc_from_string(cleaned_data.get('schemadef', ""))
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
            assignment.save() # save the assignment to recalculate any cached fields
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


@login_required
def preview_rstschemadef(request):
    if request.method == 'POST' and 'rst' in request.POST:
        rst = request.POST['rst']
        errors, values, html = input_form(rst)
        return render_to_response(
            'devilry/grade_rstschema/preview_rstschemadef.django.html', {
                'rst': html,
            }, context_instance=RequestContext(request))
    return HttpResponseBadRequest('Could not find "rst" in POST-data.')
