from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Candidate, Examiner, RelatedStudent, RelatedExaminer
from django.db import transaction

from devilry.devilry_account.models import MergedUser, PermissionGroupUser


class UserMerger:
    """
    Handles merging a ``source_user`` into a ``target_user``.

    The strategy is:

    """
    def __init__(self, source_user, target_user, pretend=True):
        self.pretend = pretend
        self.merged_user = MergedUser(
            source_user=source_user,
            target_user=target_user,
            summary_json={}
        )

    @property
    def source_user(self):
        return self.merged_user.source_user

    @property
    def target_user(self):
        return self.merged_user.target_user

    @property
    def summary(self):
        return self.merged_user.summary_json

    def _merge_user_objects(self):
        pass

    def _merge_permission_group_user_objects(self):
        permissiongroupusers = PermissionGroupUser.objects.filter(user=self.source_user)
        self.summary['PermissionGroupUser'] = {
            'note': 'Administrator permission groups. Update user foreign key so source user is replaced with target user.',
            'permission_group_user_count': permissiongroupusers.count(),
            'details': {
                'permission_group_users_updated': [
                    {
                        'permissiongroupuser_id': permissiongroupuser.id,
                        'group_name': permissiongroupuser.permissiongroup.name
                    }
                    for permissiongroupuser in permissiongroupusers.order_by('permissiongroup__name').select_related('permissiongroup')
                ]
            }
        }
        if not self.pretend:
            permissiongroupusers.update(user=self.target_user)

    def _merge_relatedstudent_objects(self):
        summary = {
            'note': 'Students on a period. Merge source RelatedStudent and all sub-objects into target RelatedStudent.',
            'relatedstudents_with_user_fk_changed_count': 0,
            'merged_relatedstudents_and_subobjects_count': 0,
            'details': {
                'merged_candidates': [],
                'merged_qualifiesforfinalexams': [],
                'relatedstudents_with_user_fk_changed': []
            }
        }
        for source_relatedstudent in RelatedStudent.objects.filter(user=self.source_user).select_related('period'):
            target_releatedstudent = RelatedStudent.objects\
                .filter(user=self.target_user, period=source_relatedstudent.period).first()
            if target_releatedstudent:

                # Candidates
                candidates = Candidate.objects.filter(relatedstudent=source_relatedstudent)\
                    .select_related('assignment_group__parentnode')
                if not self.pretend:
                    candidates.update(
                        relatedstudent=target_releatedstudent
                    )
                for candidate in candidates:
                    summary['details']['merged_candidates'].append({
                        'candidate_id': candidate.id,
                        'assignment': candidate.assignment_group.assignment.get_path()
                    })

                # QualifiesForFinalExam
                qualifiesforfinalexams = QualifiesForFinalExam.objects.filter(relatedstudent=source_relatedstudent)\
                    .select_related('relatedstudent__period')
                if not self.pretend:
                    qualifiesforfinalexams.update(
                        relatedstudent=target_releatedstudent
                    )
                for qualifiesforfinalexam in qualifiesforfinalexams:
                    summary['details']['merged_qualifiesforfinalexams'].append({
                        'qualifiesforfinalexam_id': qualifiesforfinalexam.id,
                        'period': qualifiesforfinalexam.relatedstudent.period.get_path()
                    })


                # All subobjects has been moved - delete the relatedstudent
                if not self.pretend:
                    source_relatedstudent.delete()
                summary['merged_relatedstudents_and_subobjects_count'] += 1
            else:
                if not self.pretend:
                    source_relatedstudent.user = self.target_user
                    source_relatedstudent.save()
                summary['relatedstudents_with_user_fk_changed_count'] += 1
                summary['details']['relatedstudents_with_user_fk_changed'].append({
                    'relatedstudent_id': source_relatedstudent.id,
                    'period': source_relatedstudent.period.get_path()
                })
        self.summary['RelatedStudent'] = summary


    def _merge_relatedexaminer_objects(self):
        pass

    def _merge_comment_objects(self):
        pass

    def merge(self):
        with transaction.atomic():
            self._merge_permission_group_user_objects()
            self._merge_relatedstudent_objects()
            self._merge_relatedexaminer_objects()
