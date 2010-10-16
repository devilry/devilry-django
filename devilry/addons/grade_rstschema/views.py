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
        fields = ('schemadef', 'let_students_see_schema')
        widgets = {
            'schemadef': RstSchemaDefWidget
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


@login_required
def subject_summary(request, subject_id):
    #period = get_object_or_404(Period, pk=subject_id)
    #if not subject.can_save(request.user):
        #return HttpResponseForbidden("Forbidden")
    from devilry.core.gradeplugin import registry

    def iter():
        assignment_groups = AssignmentGroup.active_where_is_candidate(
                request.user)
        assignment_groups = assignment_groups.order_by(
                "parentnode__parentnode", "parentnode__grade_plugin")
        current_period = None
        plugins = None
        for group in assignment_groups:
            if current_period == None \
                    or current_period.id != group.parentnode.parentnode.id:
                if current_period != None:
                    yield current_period, plugins
                current_period = group.parentnode.parentnode
                current_gradeplugin = None
                plugins = []
            if current_gradeplugin != group.parentnode.grade_plugin:
                current_gradeplugin = group.parentnode.grade_plugin
                plugins.append((registry.getitem(current_gradeplugin), []))
            d = group.get_latest_delivery_with_published_feedback()

            value = None
            if d:
                value = d.feedback.get_grade_as_short_string()
            else:
                value = group.get_localized_status()
            plugins[-1][1].append((group, value))
        yield current_period, plugins

    return render_to_response(
        'devilry/grade_rstschema/subject_summary.django.html', {
            'periods': iter(),
        }, context_instance=RequestContext(request))
