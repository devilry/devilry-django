from ..core import models
from can_save_authmixin import CanSaveAuthMixin
from simplified_api import simplified_api


class PublishedWhereIsExaminerMixin(object):
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        return cls._meta.model.published_where_is_examiner(user)



@simplified_api
class Subject(CanSaveAuthMixin, PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Subject
        search_resultfields = ['id', 'short_name', 'long_name']
        search_searchfields = ['short_name', 'long_name']


@simplified_api
class Period(CanSaveAuthMixin, PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Period
        search_resultfields = ['id', 'short_name', 'long_name', 'parentnode__short_name']
        search_searchfields = ['short_name', 'long_name', 'parentnode__short_name']

@simplified_api
class Assignment(CanSaveAuthMixin, PublishedWhereIsExaminerMixin):
    class Meta:
        model = models.Assignment
        search_resultfields = {
                    '__BASE__': ['id', 'short_name', 'long_name', 'parentnode__short_name'],
                    'long': ['parentnode__short_name', 'parentnode__long_name',
                        'parentnode__parentnode__long_name']}
        search_searchfields = ['short_name', 'long_name',
                'parentnode__short_name',
                'parentnode__parentnode__short_name']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        old = kwargs.pop('old', True)
        active = kwargs.pop('active', True)
        subject_short_name = kwargs.pop('subject_short_name', None)
        period_short_name = kwargs.pop('period_short_name', None)
        qryset = models.Assignment.published_where_is_examiner(user, old=old,
                active=active)
        if subject_short_name and period_short_name:
            qryset = qryset.filter(parentnode__short_name=period_short_name,
                    parentnode__parentnode__short_name=subject_short_name)
        return qryset


#class AssignmentOld(SimplifiedBase):
    #CORE_MODEL = models.Assignment

    #@classmethod
    #def search(cls, user,
            #old=True, active=True, longnamefields=False,
            #pointhandlingfields=False,
            #subject_short_name=None, period_short_name=None,
            #**standard_opts):
        #search_resultfields = ['id', 'short_name', 'long_name',
                #'parentnode__short_name',
                #'parentnode__parentnode__short_name']
        #if longnamefields:
            #search_resultfields.append('parentnode__long_name')
            #search_resultfields.append('parentnode__parentnode__long_name')
        #search_searchfields = search_resultfields
        #qryset = models.Assignment.published_where_is_examiner(user, old=old,
                #active=active)
        #if subject_short_name and period_short_name:
            #qryset = qryset.filter(parentnode__short_name=period_short_name,
                    #parentnode__parentnode__short_name=subject_short_name)
        #return cls._get(search_resultfields, search_searchfields, qryset, standard_opts)


#class Group(SimplifiedBase):
    #CORE_MODEL = models.AssignmentGroup

    #@classmethod
    #def search(cls, user,
            #assignment_id, deadlines=False, **standard_opts):
        #"""
        #List all groups in the given assignment. Provides the following
        #information (search_resultfields) for each listed group by default:

            #id
                #A unique ID for the group.
            #name
                #Name of the group, or None if it has no name.
            #canidates
                #List of username or candidate number.
            #examiners
                #List of usernames.

        #:param limit:
            #Number of results.
        #:param start:
            #Offset where the result should start (If start is 10 and
            #limit is 30, results 10 to 40 is returned, including both ends).
        #:param orderby:
            #Sort the result by this field. Must be one of:
            #*id*, *is_open*, *status*, *points*, *scaled_points* or
            #*active_deadline* (only if details is 1).
            #See :class:`devilry.core.models.AssignmentGroup` for documentation on
            #each of these search_resultfields.
        #:param deadlines:
            #Add deadlines? If True, the result will contain the following
            #additional search_resultfields:

                #deadlines
                    #A list of deadlines for this group.
                #active_deadline
                    #The active deadline for this group.
        #:param query:
            #A query to limit the results.

        #:return: The requested groups as a QuerySet.
        #"""
        #search_searchfields = ['name', 'candidates__student__username']
        #search_resultfields = ['id', 'name']
        #qryset = models.AssignmentGroup.published_where_is_examiner(user).filter(
                #parentnode=assignment_id)
        #return cls._get(search_resultfields, search_searchfields, qryset, standard_opts)
