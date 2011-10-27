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


class RelatedUsersBase(SimplifiedModelApi):
    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all related users of this type where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user, 'period', 'user', 'user__devilryuserprofile')

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.period.can_save(user):
            raise PermissionDenied()
