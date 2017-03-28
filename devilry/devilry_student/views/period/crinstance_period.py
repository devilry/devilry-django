from __future__ import unicode_literals

from django.http import Http404

from devilry.apps.core.models import Period
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_student.cradminextensions import devilry_crmenu_student
from devilry.devilry_student.views.period import overview


class Menu(devilry_crmenu_student.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        period = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_allperiods_breadcrumb_item()
        self.add_singleperiods_breadcrumb_item(period=period, active=True)


def does_not_exist_view(request):
    raise Http404()


class CrAdminInstance(devilry_crinstance.BaseCrInstanceStudent):
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
