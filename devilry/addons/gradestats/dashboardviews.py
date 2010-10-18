from django.template.loader import render_to_string
from django.template import RequestContext

from devilry.core.models import Period


def overview(request):
    where_is_admin_or_superadmin = Period.where_is_admin_or_superadmin(
            request.user)
    where_is_student = Period.objects.filter(
            assignments__assignmentgroups__candidates__student=request.user).distinct()
    if where_is_student.count() == 0 \
            and where_is_admin_or_superadmin.count() == 0:
        return None
    return render_to_string(
        'devilry/gradestats/overview.django.html', {
            'where_is_admin_or_superadmin': where_is_admin_or_superadmin,
            'where_is_student': where_is_student,
        }, context_instance=RequestContext(request))
