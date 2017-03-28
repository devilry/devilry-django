# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_group.views.download_files import batch_download_files
from devilry.devilry_group.views.examiner import feedbackfeed_examiner
from devilry.devilry_group.views.examiner import manage_deadline


class Menu(devilry_crmenu_examiner.Menu):
    devilryrole = 'examiner'

    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_assignment_breadcrumb_item(assignment=group.assignment)
        self.add_group_breadcrumb_item(group=group, active=True)


class ExaminerCrInstance(crinstance_base.DevilryGroupCrInstanceMixin, devilry_crinstance.BaseCrInstanceExaminer):
    """
    CrInstance class for examiners.
    """
    menuclass = Menu
    apps = [
        ('feedbackfeed', feedbackfeed_examiner.App),
        ('download', batch_download_files.App),
        ('manage-deadline', manage_deadline.App)
    ]
    id = 'devilry_group_examiner'

    @property
    def assignment(self):
        return self.request.cradmin_role.parentnode

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
