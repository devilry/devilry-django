from devilry.core.models import Node, Subject, Period, Assignment


def main(request):

    if request.user.is_superuser:
        is_admin = True
    else:
        is_nodeadmin = Node.where_is_admin_or_superadmin(request.user).count() > 0
        is_subjectadmin = Subject.where_is_admin_or_superadmin(request.user).count() > 0
        is_periodadmin = Period.where_is_admin_or_superadmin(request.user).count() > 0
        is_assignmentadmin = Assignment.where_is_admin_or_superadmin(request.user).count() > 0
        is_admin = True in (is_nodeadmin, is_subjectadmin, is_periodadmin,
                is_assignmentadmin)

    if not is_admin:
        return None # only show if the user is admin on at least one

    return None # will be something else here soon:)
