from django.views.generic import TemplateView
from django.conf import settings
from django_cradmin import crapp

from devilry.devilry_student.cradmin_group.utils import check_if_last_deadline_has_expired


# DEFAULT_DEADLINE_EXPIRED_MESSAGE = _(
#     'Your active deadline, %(deadline)s has expired, and the administrators of %(assignment)s '
#     'have configured HARD deadlines. This means that you can not add more deliveries to this '
#     'assignment unless an administrator extends your deadline.')
# DEADLINE_EXPIRED_MESSAGE = getattr(settings, 'DEVILRY_DEADLINE_EXPIRED_MESSAGE', DEFAULT_DEADLINE_EXPIRED_MESSAGE)


class Overview(TemplateView):
    template_name = 'devilry_student/cradmin_group/overviewapp/overview.django.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        group = self.request.cradmin_role
        context['group'] = group
        context['deadline_has_expired'] = check_if_last_deadline_has_expired(
            group=group)
        # context['deliverycount'] = context['deliveries'].count()
        context['status'] = group.get_status()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            Overview.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
