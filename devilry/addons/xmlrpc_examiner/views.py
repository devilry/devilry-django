from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from devilry.core.models import Assignment, AssignmentGroup
from devilry.xmlrpc import XmlRpc


doc = """The functions required to do the most common operations required by
a examiner."""
rpc = XmlRpc('examiner', 'devilry-xmlrpc-examiner', doc)


@rpc.rpcdec_login_required()
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
            'path': a.get_path(),
            'publishing_time': a.publishing_time,
            'deadline': a.deadline,
            }
        for a in assignments]
    return result


@rpc.rpcdec_login_required('assignment_id')
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


@rpc.rpcdec_login_required('assignmentgroup_id',
        ['The authenticated user must be examiner on the assignment group'])
def list_deliveries(request, assignmentgroup_id):
    """ Get a list (xmlrpc array) containing all deliveries within
    the given assignment group.
    
    Each entry in the list is a dict (xmlrpc structure) with the following
    values:

        id
            A number identifying the assignment-group.

        time_of_delivery
            Date/time of the delivery.

        successful
            Boolean which tells if the delivery was completed successfully.
            This might be false if the delivery was aborted midway through.

        filemetas
            List (xmlrpc array) containing a dict (xmlrpc structure) for
            each filemeta attached to the delivery. Each dict
            contains``id``, ``size`` and ``filename``.
    """
    assignment_group = get_object_or_404(AssignmentGroup,
            pk=assignmentgroup_id)
    if not assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    result = [{
            'id': d.id,
            'time_of_delivery': d.time_of_delivery,
            # TODO: Add delivered_by when it has been updated to use candidate
            'successful': d.successful,
            'filemetas': [{'id':f.id, 'filename':f.filename, 'size':f.size}
                for f in d.filemeta_set.all()]}
        for d in assignment_group.delivery_set.all()]
    return result
