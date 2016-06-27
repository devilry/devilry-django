from django.db.models.functions import Lower, Concat
from django_cradmin import crinstance
from devilry.apps.core.models import Examiner, Candidate

class CrInstanceBase(crinstance.BaseCrAdminInstance):
    """
    Base CrInstance class for crinstances in devilry_group.
    """
    def _get_candidatequeryset(self):
        """
        Get candidates.

        :return: Queryset of :class:`devilry.apps.core.models.Candidate` objects.
        """
        return Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))

    def _get_examinerqueryset(self):
        """
        Get examiners.

        :return: Queryset of :class:`devilry.apps.core.models.Examiner` objects.
        """
        return Examiner.objects\
            .select_related('relatedexaminer')\
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

    def get_titletext_for_role(self, role):
        """
        Get a short title briefly describing the given ``role``.

        :param role: :class:`devilry.apps.core.models.AssignmentGroup` object.
        :return: String representation of role.
        """
        return "{} - {}".format(role.period, role.assignment.short_name)