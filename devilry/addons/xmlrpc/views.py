from os.path import basename

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as django_login
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



USER_DISABLED = 1
SUCCESSFUL_LOGIN = 2
LOGIN_FAILED = 3


@rpc.rpcdec()
def login(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            django_login(request, user)
            return SUCCESSFUL_LOGIN
        else:
            return USER_DISABLED
    else:
        return LOGIN_FAILED


@rpc.rpcdec()
@login_required
def sum(request, a, b):
    """ Returns the sum of *a* and *b*. """
    return "Hello %s: %d" % (request.user, a + b)



@rpc.rpcdec()
@login_required
def list_assignmentgroups(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(request.user)

    assignment_groups = [{
            'id': a.id,
            'students': a.get_students(),
            'number_of_deliveries': a.get_number_of_deliveries()}
        for a in assignment_groups]
    return assignment_groups
