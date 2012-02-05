from devilry.apps.core.models import RelatedStudent, RelatedExaminer
from devilry.rest.indata import indata
from devilry.rest.restbase import RestBase

from auth import periodadmin_required


class RelatedUserDaoBase(object):
    """
    Base class for RelatedStudentDao and RelatedExaminerDao
    """
    readfields = ['id', 'tags',
                  'user_id', 'user__username', 'user__email',
                  'user__devilryuserprofile__full_name']
    corecls = None

    def _get_relatedusers(self, periodid):
        """
        Get a list of relateduser dictionaries.
        """
        return self.corecls.objects.filter(period=periodid).select_related('feedback').values(*self.readfields)

    def list(self, user, periodid):
        """
        Returns a list with one dict for each related student in the given period.

        - id --- int
        """
        periodadmin_required(user, "i18n.permissiondenied", periodid)
        return self._get_relatedusers(periodid)


class RelatedStudentDao(RelatedUserDaoBase):
    readfields = RelatedUserDaoBase.readfields + ['candidate_id']
    corecls = RelatedStudent

class RelatedExaminerDao(RelatedUserDaoBase):
    corecls = RelatedExaminer


class RestRelatedStudent(RestBase):
    def __init__(self, daocls=RelatedStudentDao, **basekwargs):
        super(RestRelatedStudent, self).__init__(**basekwargs)
        self.dao = daocls()

    @indata(assignmentid=int)
    def list(self, assignmentid):
        return self.dao.list(self.user, assignmentid)
