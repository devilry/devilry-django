from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crinstance, crmenu

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_student.cradmin_group import deliveriesapp
from . import add_deliveryapp


class Menu(crmenu.Menu):
    def build_menu(self):
        group = self.request.cradmin_role
        self.add(
            label=group.parentnode.long_name,
            url=reverse('devilry_student_period-assignments-INDEX', kwargs={
                'roleid': group.parentnode.parentnode.id
            }),
            icon="arrow-up")
        self.add(
            label=_('Add delivery'), url=self.appindex_url('add_delivery'),
            icon="home",
            active=self.request.cradmin_app.appname == 'add_delivery')
        self.add(
            label=_('Deliveries'), url=self.appindex_url('deliveries'),
            icon="home",
            active=self.request.cradmin_app.appname == 'deliveries')


class CrAdminInstance(crinstance.BaseCrAdminInstance):
    id = 'devilry_student_group'
    menuclass = Menu
    roleclass = AssignmentGroup
    rolefrontpage_appname = 'add_delivery'

    apps = [
        ('add_delivery', add_deliveryapp.App),
        ('deliveries', deliveriesapp.App),
    ]

    def get_rolequeryset(self):
        return AssignmentGroup.objects\
            .filter_student_has_access(user=self.request.user)\
            .select_related('parentnode')

    def get_titletext_for_role(self, group):
        return group.parentnode.long_name

    @classmethod
    def matches_urlpath(cls, urlpath):
        return '/devilry_student/group' in urlpath
