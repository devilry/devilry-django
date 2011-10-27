from django.contrib.auth.models import User
from django.db.models import Count, Max

from devilry.simplified import (SimplifiedModelApi, simplified_modelapi,
                                PermissionDenied, InvalidUsername, FieldSpec,
                                FilterSpecs, FilterSpec, PatternFilterSpec,
                                stringOrNoneConverter, boolConverter)
from devilry.apps.core import models
from devilry.coreutils.simplified.metabases import (SimplifiedSubjectMetaMixin,
                                                   SimplifiedPeriodMetaMixin,
                                                   SimplifiedAssignmentMetaMixin,
                                                   SimplifiedAssignmentGroupMetaMixin,
                                                   SimplifiedDeadlineMetaMixin,
                                                   SimplifiedDeliveryMetaMixin,
                                                   SimplifiedStaticFeedbackMetaMixin,
                                                   SimplifiedFileMetaMetaMixin,
                                                   SimplifiedCandidateMetaMixin)
from devilry.apps.examiner.simplified import SimplifiedDelivery as ExaminerSimplifiedDelivery

from hasadminsmixin import HasAdminsMixin
from cansavebase import CanSaveBase


@simplified_modelapi
class SimplifiedDeadline(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.Deadline`. """
    class Meta(SimplifiedDeadlineMetaMixin):
        """ Defines what methods an Administrator can use on a Deadline object using the Simplified API """
        methods = ['search', 'read', 'create', 'delete']
        editablefields = ('text', 'deadline', 'assignment_group',
                          'feedbacks_published')

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all Deadline-objects where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user).annotate(number_of_deliveries=Count('deliveries'))

    @classmethod
    def read_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` is an administrator for the given
        Deadline ``obj`` or a superadmin, and raises ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        #TODO: Replace when issue #141 is resolved!
        if not user_obj.is_superuser:
            if not obj.assignment_group.is_admin(user_obj):
                raise PermissionDenied()

    @classmethod
    def write_authorize(cls, user_obj, obj):
        """ Checks if the given ``user`` can save changes to the
        AssignmentGroup of the given Deadline ``obj``, and raises
        ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A Deadline object.
        :throws PermissionDenied:
        """
        if not obj.assignment_group.can_save(user_obj):
            raise PermissionDenied()
