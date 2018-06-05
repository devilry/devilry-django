# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from devilry.devilry_group.cradmin_instances import crinstance_base
from devilry.devilry_cradmin import devilry_crinstance
from devilry.devilry_group.views.download_files import batch_download_files
from devilry.devilry_group.views.student import feedbackfeed_student
from devilry.devilry_group.views.student import group_comment_history
from devilry.devilry_student.cradminextensions import devilry_crmenu_student
from devilry.devilry_student.views.group import projectgroupapp


class Menu(devilry_crmenu_student.Menu):
    def build_menu(self):
        super(Menu, self).build_menu()
        group = self.request.cradmin_role
        self.add_role_menuitem_object()
        self.add_allperiods_breadcrumb_item()
        self.add_singleperiods_breadcrumb_item(period=group.period)
        self.add_group_breadcrumb_item(group=group, active=True)


class StudentCrInstance(crinstance_base.DevilryGroupCrInstanceMixin, devilry_crinstance.BaseCrInstanceStudent):
    """
    CrInstance class for students.
    """
    menuclass = Menu
    apps = [
        ('projectgroup', projectgroupapp.App),
        ('feedbackfeed', feedbackfeed_student.App),
        ('commenthistory', group_comment_history.App),
        ('download', batch_download_files.App)
    ]
    id = 'devilry_group_student'

    @classmethod
    def matches_urlpath(cls, urlpath):
        return urlpath.startswith('/devilry_group/student')

    def get_rolequeryset(self):
        """
        Get the base rolequeryset from
        :func:`~devilry.devilry_group.cradmin_instances.CrInstanceBase._get_base_rolequeryset` and filter on user.

        Returns:
            QuerySet: A queryset of :class:`~devilry.apps.core.models.AssignmentGroup`s
                the ``request.user`` is student on.
        """
        return self._get_base_rolequeryset()\
            .filter_student_has_access(self.request.user)
