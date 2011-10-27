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


from helpers import _convert_list_of_usernames_to_userobjects


class HasAdminsMixin(object):
    class MetaMixin:
        fake_editablefields = ('fake_admins',)

    @classmethod
    def _parse_admins_as_list_of_usernames(cls, obj):
        """
        Parse admins as a a list of usernames. Each username must be an existing user.

        If all usernames are valid, ``obj.admins`` is cleared, and the
        given admins are added (I.E.: All current admins are replaced).
        """
        if hasattr(obj, 'fake_admins') and obj.fake_admins != None:
            users = _convert_list_of_usernames_to_userobjects(obj.fake_admins)
            obj.admins.clear()
            for user in users:
                obj.admins.add(user)

    @classmethod
    def post_save(cls, user, obj):
        cls._parse_admins_as_list_of_usernames(obj)
