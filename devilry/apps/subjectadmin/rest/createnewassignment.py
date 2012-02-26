from devilry.apps.core.models import Assignment
from auth import periodadmin_required
from devilry.rest.restbase import RestBase
from devilry.rest.indata import indata

from devilry.rest.indata import isoformatted_datetime
from devilry.rest.indata import NoneOr
from devilry.rest.indata import bool_indata


def _find_relatedexaminers_matching_tags(tags, relatedexaminers):
    examiners = []
    for relatedexaminer in relatedexaminers:
        for tag in tags:
            if relatedexaminer.tags and tag in relatedexaminer.tags:
                examiners.append(relatedexaminer.user)
    return examiners


class CreateNewAssignmentDao(object):
    def _create_assignment(self, period_id, short_name, long_name,
                           publishing_time, delivery_types, anonymous):
        assignment = Assignment(parentnode_id=period_id, short_name=short_name,
                                long_name=long_name,
                                publishing_time=publishing_time,
                                delivery_types=delivery_types,
                                anonymous=anonymous)
        assignment.full_clean()
        assignment.save()
        return assignment

    def _create_group_from_relatedstudent(self, assignment, relatedstudent,
                                          relatedexaminers):
        """
        Create an AssignmentGroup within the given ``assignment`` with tags and
        examiners from the given ``relatedstudent`` and ``relatedexaminers``.

        The examiners are set if an examiner share a tag with a student.

        Note that ``relatedexaminers`` is a parameter (as opposed to using
        assignment.parentnode...) because they should be queried for one time,
        not for each call to this method.
        """
        group = assignment.assignmentgroups.create()
        kw = dict(student=relatedstudent.user)
        if relatedstudent.candidate_id:
            kw['candidate_id'] = relatedstudent.candidate_id
        group.candidates.create(**kw)
        if relatedstudent.tags:
            tags = relatedstudent.tags.split(',')
            for tag in tags:
                group.tags.create(tag=tag)
            examiners = _find_relatedexaminers_matching_tags(tags, relatedexaminers)
            for examiner in examiners:
                group.examiners.create(user=examiner)
        return group

    def _create_deadline(self, group, deadline):
        return group.deadlines.create(deadline=deadline)

    def _add_all_relatedstudents(self, assignment, first_deadline,
                                 autosetup_examiners):
        if autosetup_examiners:
            relatedexaminers = assignment.parentnode.relatedexaminer_set.all()
        else:
            relatedexaminers = [] # If we have no related examiners, none will be added..
        for relatedstudent in assignment.parentnode.relatedstudent_set.all():
            group = self._create_group_from_relatedstudent(assignment,
                                                           relatedstudent,
                                                           relatedexaminers)
            self._create_deadline(group, first_deadline)

    def create(self, user, period_id,
               short_name, long_name, publishing_time,
               delivery_types, anonymous, add_all_relatedstudents,
               first_deadline, autosetup_examiners):
        periodadmin_required(user, "i18n.permissiondenied", period_id)
        assignment = self._create_assignment(period_id, short_name, long_name,
                                             publishing_time, delivery_types,
                                             anonymous)
        if add_all_relatedstudents:
            self._add_all_relatedstudents(assignment, first_deadline,
                                          autosetup_examiners)
        return dict(success=True)


class RestCreateNewAssignment(RestBase):
    def __init__(self, daocls=CreateNewAssignmentDao, **basekwargs):
        super(RestCreateNewAssignment, self).__init__(**basekwargs)
        self.dao = daocls()

    @indata(period_id = int,
            short_name = unicode,
            long_name = unicode,
            publishing_time = isoformatted_datetime,
            delivery_types = int,
            anonymous = bool_indata,
            add_all_relatedstudents = bool_indata,
            first_deadline = NoneOr(isoformatted_datetime),
            autosetup_examiners = bool_indata)
    def create(self, period_id,
               short_name, long_name, publishing_time,
               delivery_types, anonymous, add_all_relatedstudents,
               first_deadline, autosetup_examiners):
        return self.dao.create(self.user, period_id, short_name, long_name,
                               publishing_time, delivery_types, anonymous,
                               add_all_relatedstudents, first_deadline,
                               autosetup_examiners)
