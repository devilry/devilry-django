import re

from django_cradmin import crmenu

from devilry.devilry_student.cradminextensions import studentcrinstance
from devilry.devilry_student.views.dashboard import dashboard
from devilry.devilry_student.views.dashboard import allperiods


class Menu(crmenu.Menu):
    def build_menu(self):
        # self.add(
        #     label=_('Add delivery'),
        #     url=self.appindex_url('waitingfordeliveries'),
        #     active=self.request.cradmin_app.appname == 'waitingfordeliveries')
        # self.add(
        #     label=_('Recent deliveries'),
        #     url=self.appindex_url('recentdeliveries'),
        #     active=self.request.cradmin_app.appname == 'recentdeliveries')
        # self.add(
        #     label=_('Recent feedbacks'),
        #     url=self.appindex_url('recentfeedbacks'),
        #     active=self.request.cradmin_app.appname == 'recentfeedbacks')
        # self.add(
        #     label=_('Browse all'),
        #     url=self.appindex_url('allperiods'),
        #     active=self.request.cradmin_app.appname == 'allperiods')
        pass


class CrAdminInstance(studentcrinstance.BaseStudentCrAdminInstance):
    id = 'devilry_student'
    menuclass = Menu
    rolefrontpage_appname = 'dashboard'
    flatten_rolefrontpage_url = True

    apps = [
        ('dashboard', dashboard.App),
        ('allperiods', allperiods.App),
    ]

    def has_access(self):
        """
        We give any user access to this instance, including unauthenticated users.
        """
        return self.request.user.is_authenticated()

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return re.match('^/devilry_student/$', urlpath) or \
            re.match('^/devilry_student/allperiods/.*$', urlpath) or \
            re.match('^/devilry_student/filter/.*$', urlpath)
