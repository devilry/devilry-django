from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils.translation import ugettext as _

from devilry.core.models import Period, Assignment
from devilry.ui.messages import UiMessages
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb, DevilryLongNameWidget
from devilry.ui.fields import MultiSelectCharField
from devilry.core import gradeplugin


@login_required
def edit_assignment(request, assignment_id=None):
    isnew = assignment_id == None
    if isnew:
        assignment = Assignment()
    else:
        assignment = get_object_or_404(Assignment, id=assignment_id)
    messages = UiMessages()
    messages.load(request)

    class Form(forms.ModelForm):
        parentnode = forms.ModelChoiceField(required=True,
                queryset = Period.not_ended_where_is_admin_or_superadmin(request.user))
        admins = MultiSelectCharField(required=False,
                widget=DevilryMultiSelectFewUsersDb)
        class Meta:
            model = Assignment
            fields = ['parentnode', 'short_name', 'long_name', 
                    'publishing_time', 'filenames', 'admins']
            if isnew:
                fields.append('grade_plugin')
            widgets = {
                'publishing_time': DevilryDateTimeWidget,
                'long_name': DevilryLongNameWidget
                }

    if not isnew:
        gp = gradeplugin.registry.getitem(assignment.grade_plugin)
        msg = _('This assignment uses the <em>%(gradeplugin_label)s</em> ' \
                'grade-plugin. You cannot change grade-plugin on an ' \
                'existing assignment.' % {'gradeplugin_label': gp.label})
        if gp.admin_url_callback:
            url = gp.admin_url_callback(assignment.id)
            msg2 = _('<a href="%(gradeplugin_admin_url)s">Click here</a> '\
                    'to administer the plugin.' % {'gradeplugin_admin_url': url})
            messages.add_info('%s %s' % (msg, msg2), raw_html=True)
        else:
            messages.add_info(msg, raw_html=True)
    
    if request.method == 'POST':
        form = Form(request.POST, instance=assignment)
        if form.is_valid():
            if not assignment.can_save(request.user):
                return HttpResponseForbidden("Forbidden")
            form.save()
            messages = UiMessages()
            messages.add_success(_('Assignment successfully saved.'))
            messages.save(request)
            success_url = reverse('devilry-admin-edit_assignment',
                    args=[str(assignment.pk)])
            return HttpResponseRedirect(success_url)
    else:
        form = Form(instance=assignment)
        
    return render_to_response('devilry/admin/edit_assignment.django.html', {
        'form': form,
        'assignment': assignment,
        'messages': messages,
        'isnew': isnew,
        'gradeplugins': gradeplugin.registry.iteritems()
        }, context_instance=RequestContext(request))
