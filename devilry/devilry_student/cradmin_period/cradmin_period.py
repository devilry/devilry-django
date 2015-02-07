from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu
from django_cradmin.crinstance import reverse_cradmin_url

from devilry.apps.core.models import Period
from devilry.devilry_student.cradmin_period import assignmentsapp
from devilry.devilry_student.cradminextensions import studentcrinstance


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add_headeritem(
            label=_('Browse all'),
            url=reverse_cradmin_url(
                'devilry_student', 'allperiods', roleid=self.request.user.id),
            icon="angle-up")
        self.add(
            label=_('Assignments'),
            url=self.appindex_url('assignments'),
            icon="list",
            active=self.request.cradmin_app.appname == 'assignments')


def does_not_exist_view(request):
    raise Http404()


class CrAdminInstance(studentcrinstance.BaseStudentCrAdminInstance):
    id = 'devilry_student_period'
    menuclass = Menu
    roleclass = Period
    rolefrontpage_appname = 'assignments'

    apps = [
        ('assignments', assignmentsapp.App),
    ]

    def get_rolequeryset(self):
        return Period.objects.filter_is_candidate_or_relatedstudent(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Period.
        """
        return role.get_path()

    @classmethod
    def matches_urlpath(cls, urlpath):
        return '/devilry_student/period' in urlpath

    @classmethod
    def get_roleselect_view(cls):
        return does_not_exist_view
