from django.http import Http404
from django_cradmin import crmenu

from devilry.apps.core.models import Period
from devilry.devilry_student.cradminextensions import devilry_crinstance_student
from devilry.devilry_student.views.period import overview


class Menu(crmenu.Menu):
    def build_menu(self):
        # self.add_headeritem(
        #     label=_('Browse all'),
        #     url=reverse_cradmin_url(
        #         'devilry_student', 'allperiods', roleid=self.request.user.id),)
        # self.add(
        #     label=_('Assignments'),
        #     url=self.appindex_url('assignments'),
        #     active=self.request.cradmin_app.appname == 'assignments')
        pass


def does_not_exist_view(request):
    raise Http404()


class CrAdminInstance(devilry_crinstance_student.BaseCrInstanceStudent):
    id = 'devilry_student_period'
    menuclass = Menu
    roleclass = Period
    rolefrontpage_appname = 'overview'

    apps = [
        ('overview', overview.App),
    ]

    def get_rolequeryset(self):
        return Period.objects\
            .filter_user_is_relatedstudent(user=self.request.user)\
            .select_related('parentnode')

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
