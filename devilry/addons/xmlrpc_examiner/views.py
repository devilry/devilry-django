from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from devilry.core.models import Assignment
from devilry.xmlrpc.xmlrpc import XmlRpc


rpc = XmlRpc('examiner', 'devilry-xmlrpc-examiner')


datetime_format = '%Y-%m-%d %H:%M:%S'

@rpc.rpcdec()
@login_required
def list_active_assignments(request):
    """ Get a list (xmlrpc array) containing all active assignments where the
    authenticated user is examiner.
    
    Each entry in the list is a dict (xmlrpc structure) with the following
    values:

        id
            A number identifying the assignment.

        short_name
            The ``short_name`` of the assignment.

        long_name
            The ``long_name`` of the assignment.

        publishing_time
            The ``publishing_time`` of the assignment.

        deadline
            The ``deadline`` of the assignment.
    """
    assignments = Assignment.active_where_is_examiner(request.user)
    result = [{
            'id': a.id,
            'short_name': a.short_name,
            'long_name': a.long_name,
            'publishing_time': a.publishing_time,
            'deadline': a.deadline,
            }
        for a in assignments]
    return result


@rpc.rpcdec('assignment_id')
@login_required
def list_assignmentgroups(request, assignment_id):
    """ Get a list (xmlrpc array) containing all assignment-groups within
    the given assignment where the authenticated user is examiner.
    
    Each entry in the list is a dict (xmlrpc structure) with the following
    values:

        id
            A number identifying the assignment-group.

        students
            List of the usernames/candiatenumber of all the students on the
            group.

        number_of_deliveries
            The number of deliveries on the group.
    """
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    assignment_groups = [{
            'id': g.id,
            'students': [u.get_identifier() for u in g.candidate_set.all()],
            'number_of_deliveries': g.get_number_of_deliveries()}
        for g in assignment_groups]
    return assignment_groups
