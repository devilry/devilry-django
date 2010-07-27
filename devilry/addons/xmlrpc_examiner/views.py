from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, Http404

from devilry.core import gradeplugin_registry
from devilry.core.models import Assignment, AssignmentGroup, Delivery, \
    Feedback
from devilry.xmlrpc import XmlRpc


doc = """The functions required to do the most common operations required by
a examiner."""
rpc = XmlRpc('examiner', 'devilry-xmlrpc-examiner', doc)


@rpc.rpcdec_login_required()
def list_active_assignments(request):
    """ Get a list (xmlrpc array) containing all active assignments where the
    authenticated user is examiner.
    
    :return:
        A list where each entry is a dict (xmlrpc structure) with the
        following values:

            id
                A number identifying the assignment.

            short_name
                The ``short_name`` of the assignment.

            long_name
                The ``long_name`` of the assignment.

            path
                The unique path to the assignment.

            publishing_time
                The ``publishing_time`` of the assignment.

            xmlrpc_gradeconf
                A dict (xmlrpc struct) with the following values:

                    help
                        Help for the grade format.

                    isfile
                        True if the grade is set using a file, False
                        otherwise.

                    filename
                        The filename if ``isfile`` is True.
    """
    assignments = Assignment.active_where_is_examiner(request.user)

    def xmlrpc_gradeconf(a):
        key = a.grade_plugin
        c = gradeplugin_registry.getitem(key)
        return c.xmlrpc_gradeconf or False
    result = [{
            'id': a.id,
            'short_name': a.short_name,
            'long_name': a.long_name,
            'path': a.get_path(),
            'publishing_time': a.publishing_time,
            'xmlrpc_gradeconf': xmlrpc_gradeconf(a),
            }
        for a in assignments]
    return result


@rpc.rpcdec_login_required('assignment_path')
def list_assignmentgroups(request, assignment_path):
    """ Get a list (xmlrpc array) containing all assignment-groups within
    the given assignment where the authenticated user is examiner.

    ``assignment_path`` is the path to a assignment as a string, like
    ``"mysubject.spring09.oblig1"``.

    :return:
        A list where each entry is a dict (xmlrpc structure) with the
        following values:

            id
                A number identifying the assignment-group.

            name
                A optional name for the group.

            students
                List of the usernames/candiatenumber of all the students on the
                group.

            number_of_deliveries
                The number of deliveries on the group.
    """
    try:
        assignment = Assignment.get_by_path(assignment_path)
    except Assignment.DoesNotExist:
        raise Http404('No such assignment: %s' % assignment_path)
    except ValueError, e:
        raise Http404(str(e))

    assignment_groups = assignment.assignment_groups_where_is_examiner(
            request.user)
    assignment_groups = [{
            'id': g.id,
            'name': g.name,
            'students': [u.get_identifier() for u in g.candidates.all()],
            'deadlines': [u for u in g.deadlines.all()],
            'number_of_deliveries': g.get_number_of_deliveries()}
        for g in assignment_groups]
    return assignment_groups


@rpc.rpcdec_login_required('assignmentgroup_id',
        ['The authenticated user must be examiner on the assignment group'])
def list_deliveries(request, assignmentgroup_id):
    """ Get a list (xmlrpc array) containing all deliveries within
    the given assignment group.
    
    :return:
        A list where each entry is a dict (xmlrpc structure) with the
        following values:

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
                for f in d.filemetas.all()]}
        for d in assignment_group.deliveries.all()]
    return result


@rpc.rpcdec_login_required('delivery_id, text, format, grade',
        ['The authenticated user must be examiner on the assignment group'])
def get_feedback(request, delivery_id):
    """ Get feedback as a dict (xmlrpc structure) with the following values:

        text
            The feedback text.
        format
            The feedback format. Will always be one of:
            ``"restructuredtext"`` or ``"text"``.
        published
            True if the feedback is published, false otherwise.

    Raises fault 404 if the feedback does not exist.
    """
    delivery = get_object_or_404(Delivery,
            pk=delivery_id)
    if not delivery.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    
    try:
        feedback = delivery.feedback
    except Feedback.DoesNotExist, e:
        raise Http404(str(e))
    return dict(
            text = feedback.text,
            format = feedback.feedback_format,
            published = feedback.feedback_published)


@rpc.rpcdec_login_required('delivery_id, text, format, grade',
        ['The authenticated user must be examiner on the assignment group'])
def set_feedback(request, delivery_id, text, format, grade):
    """ Set feedback on a delivery.

    :param delivery_id:
        Id of a existing delivery.
    :param text:
        Feedback text.
    :param format:
        Feedback format. Valid values: ``"restructuredtext"`` or ``"text"``.
    :param grade:
        The grade as a string. The exact format of this value is determined
        by the grade-plugin.
    """
    delivery = get_object_or_404(Delivery,
            pk=delivery_id)
    if not delivery.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    
    try:
        feedback = delivery.feedback
    except Feedback.DoesNotExist, e:
        feedback = Feedback(delivery=delivery)
    feedback.text = text
    feedback.feedback_format = format
    feedback.set_grade_from_string(grade)
    feedback.full_clean()
    feedback.save()


@rpc.rpcdec_login_required('delivery_id, publish',
        ['The authenticated user must be examiner on the assignment group'])
def set_feedback_published(request, delivery_id, publish):
    """
    Set feedback publised to ``True`` or ``False``.
    """
    delivery = get_object_or_404(Delivery,
            pk=delivery_id)
    if not delivery.assignment_group.is_examiner(request.user):
        return HttpResponseForbidden("Forbidden")
    delivery.feedback.feedback_published = publish
    delivery.feedback.save()
