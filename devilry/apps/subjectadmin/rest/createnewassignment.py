from devilry.apps.core.models import Assignment


class CreateNewAssignmentDao(object):
    def _create_assignment(self, parentnode, short_name, long_name,
                           publishing_time, delivery_types, anonymous):
        assignment = Assignment(parentnode=parentnode, short_name=short_name,
                                long_name=long_name,
                                publishing_time=publishing_time,
                                delivery_types=delivery_types,
                                anonymous=anonymous)
        assignment.full_clean()
        assignment.save()
        return assignment

    def _add_all_relatedstudents(self, assignment, first_deadline):
        for relatedstudent in assignment.parentnode.relatedstudent_set.all():
            group = assignment.assignmentgroups.create()
            group.save()
            kw = dict(student=relatedstudent.user)
            if relatedstudent.candidate_id:
                kw['candidate_id'] = relatedstudent.candidate_id
            group.candidates.create(**kw)

    def create_noauth(self, parentnode, short_name, long_name, publishing_time,
                      delivery_types, anonymous, add_all_relatedstudents,
                      first_deadline, autosetup_examiners):
        assignment = self._create_assignment(parentnode, short_name, long_name,
                                             publishing_time, delivery_types,
                                             anonymous)
        if add_all_relatedstudents:
            self._add_all_relatedstudents(assignment, first_deadline)
