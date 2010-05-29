from os.path import basename
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.formsets import formset_factory
from devilry.core.models import (Delivery, Feedback, AssignmentGroup,
        Node, Subject, Period, Assignment, FileMeta)
from devilry.core import gradeplugin_registry
from django.db import transaction

from devilry.core.xmlrpc import XmlRpc
from devilry.core.utils.GroupNodes import group_assignments, group_assignmentgroups 


rpc = XmlRpc()


@rpc.rpcdec()
def sum(request, a, b):
    """ Returns the sum of *a* and *b*. """
    return "Hello %s: %d" % (request.user, a + b)



#@login_required

@rpc.rpcdec()
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(request.user)
    if assignment_groups:
        assignment = assignment_groups[0].parentnode
    else:
        assignment = None

    return dict(
        assignment = assignment,
        assignment_groups = assignment_groups)
