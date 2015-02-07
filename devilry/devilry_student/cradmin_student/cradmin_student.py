from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu

from devilry.devilry_student.cradminextensions import studentcrinstance
from devilry.devilry_student.cradmin_student import waitingfordeliveriesapp
from devilry.devilry_student.cradmin_student import recentdeliveriesapp
from devilry.devilry_student.cradmin_student import recentfeedbacksapp
from devilry.devilry_student.cradmin_student import allperiodsapp


class Menu(crmenu.Menu):
    def build_menu(self):
        self.add(
            label=_('Add delivery'),
            url=self.appindex_url('waitingfordeliveries'),
            icon="plus",
            active=self.request.cradmin_app.appname == 'waitingfordeliveries')
        self.add(
            label=_('Recent deliveries'),
            url=self.appindex_url('recentdeliveries'),
            icon="th-list",
            active=self.request.cradmin_app.appname == 'recentdeliveries')
        self.add(
            label=_('Recent feedbacks'),
            url=self.appindex_url('recentfeedbacks'),
            icon="th-list",
            active=self.request.cradmin_app.appname == 'recentfeedbacks')
        self.add(
            label=_('Browse all'),
            url=self.appindex_url('allperiods'),
            icon="th-list",
            active=self.request.cradmin_app.appname == 'allperiods')


class CrAdminInstance(studentcrinstance.BaseStudentCrAdminInstance):
    id = 'devilry_student'
    menuclass = Menu
    roleclass = get_user_model()
    rolefrontpage_appname = 'waitingfordeliveries'

    apps = [
        ('waitingfordeliveries', waitingfordeliveriesapp.App),
        ('recentdeliveries', recentdeliveriesapp.App),
        ('recentfeedbacks', recentfeedbacksapp.App),
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
