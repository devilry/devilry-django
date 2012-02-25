from devilry.apps.core.models import Assignment


class CreateNewAssignmentDao(object):
    def _create_assignment(self, parentnode, short_name, long_name, publishing_time,
                           delivery_types, anonymous):
        assignment = Assignment(parentnode=parentnode, short_name=short_name,
                                long_name=long_name, publishing_time=publishing_time,
                                delivery_types=delivery_types, anonymous=anonymous)
        assignment.full_clean()
        assignment.save()
        return assignment

    def create_noauth(self, parentnode, short_name, long_name, publishing_time,
                      delivery_types, anonymous, add_all_relatedstudents,
                      first_deadline, autosetup_examiners):
        assignment = self._create_assignment(parentnode, short_name, long_name, publishing_time,
                                             delivery_types, anonymous)
