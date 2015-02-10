from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crmenu

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_student.cradminextensions import studentcrinstance
from devilry.devilry_student.cradmin_group import overviewapp
from devilry.devilry_student.cradmin_group import deliveriesapp
from devilry.devilry_student.cradmin_group import projectgroupapp
from devilry.devilry_student.cradmin_group import contactapp


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add_headeritem(
            label=group.subject.long_name,
            url=reverse('devilry_student_period-assignments-INDEX', kwargs={
                'roleid': group.parentnode.parentnode.id
            }),
            icon="angle-up")
        self.add(
            label=_('Overview'), url=self.appindex_url('overview'),
            icon="info-circle",
            active=self.request.cradmin_app.appname == 'overview')
        self.add(
            label=_('Deliveries'), url=self.appindex_url('deliveries'),
            icon="th-list",
            active=self.request.cradmin_app.appname == 'deliveries')

        if not group.assignment.anonymous:
            self.add(
                label=_('Contact examiner'), url=self.appindex_url('contact'),
                icon="envelope",
                active=self.request.cradmin_app.appname == 'contact')

        if group.assignment.students_can_create_groups:
            self.add(
                label=_('Project group'), url=self.appindex_url('projectgroup'),
                icon="users",
                active=self.request.cradmin_app.appname == 'projectgroup')


class CrAdminInstance(studentcrinstance.BaseStudentCrAdminInstance):
    id = 'devilry_student_group'
    menuclass = Menu
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'overview'

    apps = [
        ('overview', overviewapp.App),
        ('deliveries', deliveriesapp.App),
        ('projectgroup', projectgroupapp.App),
        ('contact', contactapp.App),
    ]

    def get_rolequeryset(self):
        return AssignmentGroup.objects\
            .filter_student_has_access(user=self.request.user)\
            .annotate_with_last_deadline_pk()\
            .annotate_with_last_deadline_datetime()\
            .select_related('parentnode')

    def get_role_from_rolequeryset(self, role):
        role = super(CrAdminInstance, self).get_role_from_rolequeryset(role)
        if role.last_deadline_pk is None:
            raise Http404()
        return role

    def get_titletext_for_role(self, group):
        return group.parentnode.long_name

    @classmethod
    def matches_urlpath(cls, urlpath):
        return '/devilry_student/group' in urlpath
