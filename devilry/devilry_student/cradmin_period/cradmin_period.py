from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu

from devilry.apps.core.models import Period
from devilry.devilry_student.cradmin_period import assignments
from devilry.devilry_student.cradminextensions import studentcrinstance


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add(
            label=_('Assignments'), url=self.appindex_url('assignments'), icon="home",
            active=self.request.cradmin_app.appname == 'assignments')


class CrAdminInstance(studentcrinstance.BaseStudentCrAdminInstance):
    id = 'devilry_student_period'
    menuclass = Menu
    roleclass = Period
    rolefrontpage_appname = 'assignments'

    apps = [
        ('assignments', assignments.App),
    ]

    def get_rolequeryset(self):
        return Period.objects.filter_is_candidate_or_relatedstudent(user=self.request.user)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a Site.
        """
        return role.get_path()

    @classmethod
    def matches_urlpath(cls, urlpath):
        return '/devilry_student/period' in urlpath
