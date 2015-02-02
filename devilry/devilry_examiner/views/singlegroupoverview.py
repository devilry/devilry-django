from django.views.generic import DetailView
#from django.http import Http404

from devilry.apps.core.models import AssignmentGroup


def get_previous_and_next_group_waiting_for_feedback(examineruser, current_group):
    groups = AssignmentGroup.objects\
        .filter_waiting_for_feedback()\
        .filter_examiner_has_access(examineruser)\
        .filter(parentnode=current_group.parentnode)\
        .annotate_with_last_deadline_datetime()\
        .annotate_with_last_delivery_time_of_delivery()\
        .extra(order_by=['last_deadline_datetime', 'last_delivery_time_of_delivery'])
    use_next = False
    next = None
    previous = None
    if groups.filter(pk=current_group.pk).exists():
        for group in groups:
            if use_next:
                next = group
                break

            if group == current_group:
                use_next = True
            else:
                previous = group
    else:
        groups = list(groups)
        if len(groups) > 0:
            next = groups[0]
    return previous, next


class SingleGroupOverview(DetailView):
    template_name = "devilry_examiner/singlegroupoverview.django.html"
    model = AssignmentGroup
    pk_url_kwarg = 'groupid'
    context_object_name = 'group'

    def get_queryset(self):
        return AssignmentGroup.objects.filter_examiner_has_access(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SingleGroupOverview, self).get_context_data(**kwargs)
        previous, next = get_previous_and_next_group_waiting_for_feedback(
            self.request.user, self.object)
        context['previous_group_waiting_for_feedback'] = previous
        context['next_group_waiting_for_feedback'] = next
        return context
