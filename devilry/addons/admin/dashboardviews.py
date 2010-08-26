from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from devilry.core.models import Node, Subject, Period, Assignment


def list_nodes_generic(request, nodecls, headings, deletemessage,
        help_text=None):
    clsname = nodecls.__name__.lower()
    return render_to_string('devilry/admin/dashboard/list_nodes.django.html', {
            'jsonurl': reverse('admin-autocomplete-%sname' % clsname),
            'createurl': reverse('devilry-admin-create_%s' % clsname),
            'deleteurl': reverse('devilry-admin-delete_many%ss' % clsname),
            'headings': headings,
            'deletemessage': deletemessage,
            'clsname': clsname,
            'help': help_text
        }, context_instance=RequestContext(request))

def list_nodes(request, *args, **kwargs):
    return list_nodes_generic(request, Node,
            headings = ["Node", "Administrators"],
            deletemessage = \
                _('This will delete all selected nodes and all subjects, periods, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            help_text = \
                _('A node at the top of the navigation tree. It is a '\
                'generic element used to organize administrators. A '\
                'Node can be organized below another Node, and it can '\
                'only have one parent.'))

def list_subjects(request, *args, **kwargs):
    return list_nodes_generic(request, Subject,
            headings = ["Subject", "Administrators"],
            deletemessage = \
                _('This will delete all selected subjects and all periods, '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            help_text = \
                _('A subject is a course, seminar, class or something '\
                'else being given regularly. A subject is further '\
                'divided into periods.'))

def list_periods(request, *args, **kwargs):
    return list_nodes_generic(request, Period,
            headings = ["Subject", "Period", "Start time", "Administrators"],
            deletemessage = \
                _('This will delete all selected periods and all '\
                'assignments, assignment groups, deliveries and feedbacks within '\
                'them.'),
            help_text = \
                _('A Period is a limited period of time within a subject, '
                'like "spring 2009", "week 34 2010" or even a single day.'))

def list_assignments(request, *args, **kwargs):
    return list_nodes_generic(request, Assignment,
            headings = ["Assignment",
                    "Publishing time", "Administrators"],
            deletemessage = \
                _('This will delete all selected assignments and all '\
                'assignment groups, deliveries and feedbacks within '\
                'them.'),
            help_text = \
                 _('An assignment within a period.'))
