from django.contrib.auth import get_user_model
from django_cradmin import crmenu

from devilry.devilry_student.views.cradmin_student import allperiodsapp
from devilry.devilry_student.cradminextensions import studentcrinstance


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
    roleclass = get_user_model()
    rolefrontpage_appname = 'waitingfordeliveries'

    apps = [
        ('allperiods', allperiodsapp.App),
    ]

    def get_rolequeryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.
        Remember that the role is a User.
        """
        return str(role.id)

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_student/')
