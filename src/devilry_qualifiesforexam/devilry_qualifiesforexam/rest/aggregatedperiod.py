from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Period
from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import RelatedStudentKeyValue



class PermissionDeniedError(ErrorResponse):
    def __init__(self, errormsg):
        super(PermissionDeniedError, self).__init__(status.HTTP_403_FORBIDDEN,
                                                    {'detail': errormsg})



class IsPeriodAdmin(BasePermission):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on the period given as the id kwarg to the
    view.
    """
    def get_id(self):
        """
        Get the ``id`` from the view kwargs.

        :raise PermissionDeniedError: If the ``id`` can not be determined.
        """
        try:
            return self.view.kwargs['id']
        except KeyError, e:
            raise PermissionDeniedError(('The {classname} permission checker '
                                         'requires the ``id`` parameter.').format(classname=self.__class__.__name__))

    def check_permission(self, user):
        if user.is_superuser:
            return
        periodid = self.get_id()
        if Period.where_is_admin_or_superadmin(user).filter(id=periodid).count() == 0:
            raise PermissionDeniedError('Permission denied')




class AggregatePeriod(View):
    """
    Get detailed data for all students on a period, including their labels.

    # Parameters
    - ``id``: The last part of the path is the ID of the period.
    - ``load_everything``: Add ``load_everything=1`` to the querystring to
      load feedback for all groups for all students within the period.
    - ``include_nonrelated``: Add ``include_nonrelated=1`` to the querystring
      to include students that are not registered as related students on the
      period (but are registered as candidate on a group). Ignored unless
      ``load_everything=1``.

    # Returns
    An object/dict with one item for each student on the period. Each item
    has the following attributes:

    - ``userid``: The ID of the Devilry user for the student. This is unique within a period.
    - ``user``: An object with the following attributes:
        - ``id``: The same as ``userid``.
        - ``username``
        - ``email``
        - ``full_name``
    - ``relatedstudent``: An object with details about the RelatedStudent.
      If ``include_nonrelated=1`` (se parameters), the value of this attribute
      is ``null`` for students registered on a group, but not on the period. The
      object has the following attributes:
        - ``id``: ID of the RelatedStudent.
        - ``tags``
        - ``candidate_id``
        - ``labels``: Labels are RelatedStudentKeyValue objects with
          ``application=devilry.statistics.Labels``. An object with the
          following attributes:
            ``id``: ID of the RelatedStudentKeyValue.
            ``label``: A string.
    - ``groups``: ``null`` if ``load_everything!=1`` (see parameters). List of groups where the
      user (student) is candidate. Each item in list has the following
      attributes:
        - ``id``
        - ``is_open``
        - ``assignment_id``
        - ``feedback``: An object with the following attributes:
            - ``id``
            - ``grade``
            - ``points``
            - ``is_passing_grade``
            - ``save_timestamp``
    """
    permissions = (IsAuthenticated, IsPeriodAdmin)

    def _serialize_user(self, user):
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.devilryuserprofile.full_name}

    def _serialize_relatedstudent(self, relatedstudent):
        return {'id': relatedstudent.id,
                'tags': relatedstudent.tags,
                'candidate_id': relatedstudent.candidate_id,
                'labels': []
               }

    def _serialize_feedback(self, feedback):
        if feedback:
            return {'id': feedback.id,
                    'grade': feedback.grade,
                    'points': feedback.points,
                    'is_passing_grade': feedback.is_passing_grade,
                    'save_timestamp': feedback.save_timestamp}
        else:
            return None

    def _serialize_group(self, group):
        return {'id': group.id,
                'is_open': group.is_open,
                'assignment_id': group.parentnode_id,
                'feedback': self._serialize_feedback(group.feedback)}

    def _create_resultdict(self, user, relatedstudent=None):
        resultdict = {'userid': user.id, # Needed by ExtJS since an object can not be idProperty on a model - does not hurt in any other cases even if it is also included in ``user``.
                      'user': self._serialize_user(user),
                      'relatedstudent': None,
                      'groups': []}
        if relatedstudent:
            resultdict['relatedstudent'] = self._serialize_relatedstudent(relatedstudent)
        return resultdict

    def _initialize_from_relatedstudents(self, period):
        relatedstudents = RelatedStudent.objects.filter(period=period)
        relatedstudents = relatedstudents.select_related('user', 'user__devilryuserprofile')
        result = {}
        for relatedstudent in relatedstudents:
            result[str(relatedstudent.user.id)] = self._create_resultdict(relatedstudent.user, relatedstudent)
        return result

    def _add_labels(self, period, result):
        keyvalues = RelatedStudentKeyValue.objects.filter(relatedstudent__period=period,
                                                          application='devilry.statistics.Labels')
        keyvalues = keyvalues.select_related('relatedstudent')
        for keyvalue in keyvalues:
            userdct = result[str(keyvalue.relatedstudent.user_id)]
            userdct['relatedstudent']['labels'].append({'id': keyvalue.id,
                                                        'label': keyvalue.key})


    def _add_groups(self, period, result, include_nonrelated):
        groups = AssignmentGroup.objects.filter(parentnode__parentnode=period)
        groups = groups.select_related('feedback')
        groups = groups.prefetch_related('candidates', 'candidates__student',
                                         'candidates__student__devilryuserprofile')
        groups = groups.order_by('parentnode__publishing_time')
        for group in groups:
            groupdct = self._serialize_group(group)
            for candidate in group.candidates.all():
                user = candidate.student
                userkey = str(user.id)
                try:
                    userdct = result[userkey]
                except KeyError:
                    # NOTE: This means that we have a student registered on an assignment, but not on the period. These are not handled by the old Admin-ui, bu should be handled in the new.
                    if include_nonrelated:
                        userdct = self._create_resultdict(user)
                        result[userkey] = userdct
                        userdct['groups'].append(groupdct)
                else:
                    userdct['groups'].append(groupdct)

    def get(self, request, id):
        period = Period.objects.get(pk=id)
        result = self._initialize_from_relatedstudents(period)
        self._add_labels(period, result)
        load_everything = request.GET.get('load_everything', None) == '1'

        if load_everything:
            include_nonrelated = request.GET.get('include_nonrelated', None) == '1'
            self._add_groups(period, result, include_nonrelated)
        return result.values()
