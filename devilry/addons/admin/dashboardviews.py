from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from devilry.core.models import Node, Subject, Period, Assignment


def list_nodes_generic(request, nodecls, headings, deletemessage):
    clsname = nodecls.__name__.lower()
    return render_to_string('devilry/admin/dashboard/list_nodes.django.html', {
            'jsonurl': reverse('admin-autocomplete-%sname' % clsname),
            'createurl': reverse('devilry-admin-create_%s' % clsname),
            'deleteurl': reverse('devilry-admin-delete_many%ss' % clsname),
            'headings': headings,
            'deletemessage': deletemessage,
            'clsname': clsname
        }, context_instance=RequestContext(request))

def list_nodes(request, *args, **kwargs):
    return list_nodes_generic(request, Node,
            ["Node"],
            _('This will delete all selected nodes and all subjects, periods, '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def list_subjects(request, *args, **kwargs):
    return list_nodes_generic(request, Subject,
            ["Subject"],
            _('This will delete all selected subjects and all periods, '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def list_periods(request, *args, **kwargs):
    return list_nodes_generic(request, Period,
            ["Subject", "Period"],
            _('This will delete all selected periods and all '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def list_assignments(request, *args, **kwargs):
    return list_nodes_generic(request, Assignment,
            ["Subject", "Period", "Assignment"],
            _('This will delete all selected assignments and all '\
            'assignment groups, deliveries and feedbacks within '\
            'them.'))
