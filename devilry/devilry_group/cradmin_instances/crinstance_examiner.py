# Python imports
from __future__ import unicode_literals

# Devilry/cradmin imports
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views.examiner import feedbackfeed_examiner


class Menu(devilry_crmenu_examiner.Menu):
    devilryrole = 'examiner'

    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_assignment_breadcrumb_item(assignment=group.assignment)
        self.add_group_breadcrumb_item(group=group, active=True)


class ExaminerCrInstance(crinstance_base.CrInstanceBase):
    """
    CrInstance class for examiners.
    """
    menuclass = Menu
    apps = [
        ('feedbackfeed', feedbackfeed_examiner.App)
    ]
    id = 'devilry_group_examiner'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/examiner')

    def get_rolequeryset(self):
        """
        Get the base rolequeryset from
        :func:`~devilry.devilry_group.cradmin_instances.CrInstanceBase._get_base_rolequeryset` and filter on user.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s
                the ``request.user`` is examiner on.
        """
        return self._get_base_rolequeryset()\
            .filter_examiner_has_access(self.request.user)

    def get_devilryrole_for_requestuser(self):
        """
        Get the role of the user.

        Returns:
            str: ``examiner`` as devilryrole.
        """
        return 'examiner'
