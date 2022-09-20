

from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from django.views.generic import View
from django.http import HttpResponseRedirect, Http404

from devilry.apps.core.models import Subject


class SubjectRedirectView(View):
    """
    Redirects subject admin to full subject overview, and period admins to a more simpler view.
    """
    def dispatch(self, request, *args, **kwargs):
        if Subject.objects.filter_user_is_admin(self.request.user).filter(id=request.cradmin_role.id).exists():
            return HttpResponseRedirect(reverse_cradmin_url(
                instanceid='devilry_admin_subjectadmin',
                appname='overview',
                roleid=request.cradmin_role.id
            ))
        elif Subject.objects.filter_user_is_admin_for_any_periods_within_subject(self.request.user).filter(id=request.cradmin_role.id).exists():
            return HttpResponseRedirect(str(self.request.cradmin_instance.rolefrontpage_url(roleid=request.cradmin_role.id)))
        raise Http404()


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', SubjectRedirectView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
