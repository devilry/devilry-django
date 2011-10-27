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


@simplified_modelapi
class SimplifiedRelatedStudentKeyValue(SimplifiedModelApi):
    """ Simplified wrapper for :class:`devilry.apps.core.models.RelatedStudentKeyValue`. """
    class Meta:
        model = models.RelatedStudentKeyValue
        methods = ['create', 'read', 'update', 'delete', 'search']
        resultfields = FieldSpec('id', 'application', 'key', 'value', 'relatedstudent', 'student_can_read')
        searchfields = FieldSpec('application', 'key', 'value', 'relatedstudent__user__username')
        editablefields = ('application', 'key', 'value', 'relatedstudent', 'student_can_read')
        filters = FilterSpecs(FilterSpec('id', supported_comp=('exact',)),
                              FilterSpec('student_can_read', supported_comp=('exact',), type_converter=boolConverter),
                              FilterSpec('application', supported_comp=('exact',)),
                              FilterSpec('relatedstudent__period', supported_comp=('exact',)),
                              FilterSpec('relatedstudent__user', supported_comp=('exact',)))

    @classmethod
    def create_searchqryset(cls, user):
        """ Returns all related users of this type where given ``user`` is admin or superadmin.

        :param user: A django user object.
        :rtype: a django queryset
        """
        return cls._meta.model.where_is_admin_or_superadmin(user)

    @classmethod
    def write_authorize(cls, user, obj):
        """ Check if the given ``user`` can save changes to the given
        ``obj``, and raise ``PermissionDenied`` if not.

        :param user: A django user object.
        :param obj: A object of the type this method is used in.
        :throws PermissionDenied:
        """
        if not obj.relatedstudent.period.can_save(user):
            raise PermissionDenied()

    @classmethod
    def is_empty(cls, obj):
        return True
