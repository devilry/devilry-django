from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models

from devilry.devilry_merge_v3database.models import TempMergeId
from devilry.devilry_merge_v3database.utils import assignment_group_merger
from devilry.devilry_merge_v3database.tests.utils import MergerTestHelper


class TestAssignmentGroupMerger(MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                with_assignment_group=False, assignment_group_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        if with_assignment_group:
            self.get_or_create_assignment_group(assignment=assignment, assignment_group_kwargs=assignment_group_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'migrate_group'}
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs, db_alias=self.from_db_alias)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs, db_alias=self.from_db_alias)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs,
                                                   db_alias=self.from_db_alias)
        self.get_or_create_assignment_group(assignment=assignment,
                                            assignment_group_kwargs=assignment_group_kwargs,
                                            db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_assignment_group=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(core_models.AssignmentGroup.objects.count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.get().name, 'default_group')
        self.assertEqual(core_models.AssignmentGroup.objects.get().parentnode.short_name, 'default_assignment')
        self.assertEqual(core_models.AssignmentGroup.objects.get().parentnode.parentnode.short_name, 'default_period')
        self.assertEqual(core_models.AssignmentGroup.objects.get().parentnode.parentnode.parentnode.short_name,
                         'default_subject')

        # Test migrate database
        migrate_db_queryset = core_models.AssignmentGroup.objects.using(self.from_db_alias)
        self.assertEqual(migrate_db_queryset.count(), 1)
        self.assertEqual(migrate_db_queryset.get().name, 'migrate_group')
        self.assertEqual(migrate_db_queryset.get().parentnode.short_name, 'migrate_assignment')
        self.assertEqual(migrate_db_queryset.get().parentnode.parentnode.short_name, 'migrate_period')
        self.assertEqual(migrate_db_queryset.get().parentnode.parentnode.parentnode.short_name,
                         'migrate_subject')

    def test_assignment_group_not_imported(self):
        # Default database data
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'})

        # Migrate database
        self.__create_for_migrate_db()

        with self.assertRaisesMessage(ValueError, 'Assignments must be imported before AssignmentGroups.'):
            assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_check_existing_assignment_group_not_affected(self):
        # Default database data
        default_etag = timezone.now() - timezone.timedelta(days=10)
        default_created_datetime = timezone.now() - timezone.timedelta(days=5)
        default_assignment_group_kwargs = {
            'name': 'default_group',
            'is_open': True,
            'etag': default_etag,
            'created_datetime': default_created_datetime,
            'internal_is_being_deleted': True
        }
        self.__create_for_default_db(with_assignment_group=True,
                                     assignment_group_kwargs=default_assignment_group_kwargs)
        core_models.AssignmentGroup.objects.filter(name='default_group').update(etag=default_etag)
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'})

        # Migrate database data
        migrate_etag = timezone.now() - timezone.timedelta(days=20)
        migrate_created_datetime = timezone.now() - timezone.timedelta(days=15)
        migrate_assignment_group_kwargs = {
            'name': 'migrate_group',
            'is_open': False,
            'etag': migrate_etag,
            'created_datetime': migrate_created_datetime,
            'internal_is_being_deleted': False
        }
        self.__create_for_migrate_db(assignment_group_kwargs=migrate_assignment_group_kwargs)
        core_models.AssignmentGroup.objects.using(self.from_db_alias).filter(name='migrate_group')\
            .update(etag=migrate_etag)

        self.assertEqual(core_models.AssignmentGroup.objects.count(), 1)
        assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.AssignmentGroup.objects.count(), 2)

        # Test default group
        default_group = core_models.AssignmentGroup.objects.get(name='default_group')
        self.assertEqual(default_group.parentnode.short_name, 'default_assignment')
        self.assertEqual(default_group.parentnode.parentnode.short_name, 'default_period')
        self.assertEqual(default_group.parentnode.parentnode.parentnode.short_name, 'default_subject')
        self.assertTrue(default_group.is_open)
        self.assertEqual(default_group.etag, default_etag)
        self.assertEqual(default_group.created_datetime, default_created_datetime)
        self.assertTrue(default_group.internal_is_being_deleted)

        # Test migrated group
        migrated_group = core_models.AssignmentGroup.objects.get(name='migrate_group')
        self.assertEqual(migrated_group.parentnode.short_name, 'migrate_assignment')
        self.assertEqual(migrated_group.parentnode.parentnode.short_name, 'migrate_period')
        self.assertEqual(migrated_group.parentnode.parentnode.parentnode.short_name, 'migrate_subject')
        self.assertFalse(migrated_group.is_open)
        self.assertEqual(migrated_group.etag, migrate_etag)
        self.assertEqual(migrated_group.created_datetime, migrate_created_datetime)
        self.assertFalse(migrated_group.internal_is_being_deleted)

    def test_import_multiple_assignment_groups_on_same_assignment_as_existing_group(self):
        # Default database data
        self.__create_for_default_db(subject_kwargs={'short_name': 'migrate_subject'},
                                     period_kwargs={'short_name': 'migrate_period'},
                                     assignment_kwargs={'short_name': 'migrate_assignment'},
                                     with_assignment_group=True, assignment_group_kwargs={'name': 'default_group'})

        # Migrate database data
        migrate_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'}
        }
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group1'}, **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group2'}, **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group3'}, **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group4'}, **migrate_db_kwarg_data)

        self.assertEqual(core_models.AssignmentGroup.objects.count(), 1)
        assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.AssignmentGroup.objects.count(), 5)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='default_group').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='default_group').get().parentnode.short_name,
                         'migrate_assignment')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group1').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group1').get().parentnode.short_name,
                         'migrate_assignment')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group2').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group2').get().parentnode.short_name,
                         'migrate_assignment')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group3').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group3').get().parentnode.short_name,
                         'migrate_assignment')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group4').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group4').get().parentnode.short_name,
                         'migrate_assignment')

    def test_import_multiple_assignment_groups_on_different_assignments(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
        }
        self.__create_for_default_db(assignment_kwargs={'short_name': 'migrate_assignment1'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_kwargs={'short_name': 'migrate_assignment2'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_kwargs={'short_name': 'migrate_assignment3'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_kwargs={'short_name': 'migrate_assignment4'}, **default_db_kwarg_data)

        # Migrate database data
        migrate_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
        }
        self.__create_for_migrate_db(assignment_kwargs={'short_name': 'migrate_assignment1'},
                                     assignment_group_kwargs={'name': 'migrate_group1'},
                                     **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_kwargs={'short_name': 'migrate_assignment2'},
                                     assignment_group_kwargs={'name': 'migrate_group2'},
                                     **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_kwargs={'short_name': 'migrate_assignment3'},
                                     assignment_group_kwargs={'name': 'migrate_group3'},
                                     **migrate_db_kwarg_data)
        self.__create_for_migrate_db(assignment_kwargs={'short_name': 'migrate_assignment4'},
                                     assignment_group_kwargs={'name': 'migrate_group4'},
                                     **migrate_db_kwarg_data)

        self.assertEqual(core_models.AssignmentGroup.objects.count(), 0)
        assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.AssignmentGroup.objects.count(), 4)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group1').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group1').get().parentnode.short_name,
                         'migrate_assignment1')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group2').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group2').get().parentnode.short_name,
                         'migrate_assignment2')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group3').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group3').get().parentnode.short_name,
                         'migrate_assignment3')
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group4').count(), 1)
        self.assertEqual(core_models.AssignmentGroup.objects.filter(name='migrate_group4').get().parentnode.short_name,
                         'migrate_assignment4')

    def test_single_temp_merge_id_created(self):
        # Default database data
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'})

        # Migrate database data
        self.__create_for_migrate_db(assignment_group_kwargs={'id': 250, 'name': 'migrate_group'})

        self.assertEqual(TempMergeId.objects.count(), 0)
        assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(TempMergeId.objects.count(), 1)
        temp_merge_id = TempMergeId.objects.get()
        self.assertEqual(temp_merge_id.from_id, 250)
        self.assertEqual(temp_merge_id.model_name, 'core_assignmentgroup')
        self.assertTrue(core_models.AssignmentGroup.objects.filter(id=temp_merge_id.to_id).count(), 1)

    def test_multiple_temp_merge_ids_created(self):
        # Default database data
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'})

        # Migrate database data
        migrate_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'}
        }
        self.__create_for_migrate_db(
            assignment_group_kwargs={'id': 200, 'name': 'migrate_group1'},
            **migrate_db_kwarg_data
        )
        self.__create_for_migrate_db(
            assignment_group_kwargs={'id': 250, 'name': 'migrate_group2'},
            **migrate_db_kwarg_data
        )
        self.__create_for_migrate_db(
            assignment_group_kwargs={'id': 300, 'name': 'migrate_group3'},
            **migrate_db_kwarg_data
        )
        self.__create_for_migrate_db(
            assignment_group_kwargs={'id': 350, 'name': 'migrate_group4'},
            **migrate_db_kwarg_data
        )

        self.assertEqual(TempMergeId.objects.count(), 0)
        assignment_group_merger.AssignmentGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(TempMergeId.objects.count(), 4)

        temp_merge_id_group1 = TempMergeId.objects.get(from_id=200)
        self.assertEqual(temp_merge_id_group1.model_name, 'core_assignmentgroup')
        group1_from_temp_merge_id = core_models.AssignmentGroup.objects.get(id=temp_merge_id_group1.to_id)
        self.assertEqual(group1_from_temp_merge_id.name, 'migrate_group1')

        temp_merge_id_group2 = TempMergeId.objects.get(from_id=250)
        self.assertEqual(temp_merge_id_group2.model_name, 'core_assignmentgroup')
        group2_from_temp_merge_id = core_models.AssignmentGroup.objects.get(id=temp_merge_id_group2.to_id)
        self.assertEqual(group2_from_temp_merge_id.name, 'migrate_group2')

        temp_merge_id_group3 = TempMergeId.objects.get(from_id=300)
        self.assertEqual(temp_merge_id_group3.model_name, 'core_assignmentgroup')
        group3_from_temp_merge_id = core_models.AssignmentGroup.objects.get(id=temp_merge_id_group3.to_id)
        self.assertEqual(group3_from_temp_merge_id.name, 'migrate_group3')

        temp_merge_id_group4 = TempMergeId.objects.get(from_id=350)
        self.assertEqual(temp_merge_id_group4.model_name, 'core_assignmentgroup')
        group4_from_temp_merge_id = core_models.AssignmentGroup.objects.get(id=temp_merge_id_group4.to_id)
        self.assertEqual(group4_from_temp_merge_id.name, 'migrate_group4')


class TestCandidateMerger(MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, user_kwargs=None,
                                with_candidate=False, candidate_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment_group = self.get_or_create_assignment_group(assignment=assignment,
                                                               assignment_group_kwargs=assignment_group_kwargs)
        user = self.get_or_create_user(user_kwargs=user_kwargs)
        related_student = self.get_or_create_related_student(user=user, period=period)
        if with_candidate:
            self.get_or_create_candidate(assignment_group=assignment_group, related_student=related_student,
                                         candidate_kwargs=candidate_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, user_kwargs=None, candidate_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'migrate_group'}
        if not user_kwargs:
            user_kwargs = {'shortname': 'migrate_user'}
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs, db_alias=self.from_db_alias)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs, db_alias=self.from_db_alias)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs,
                                                   db_alias=self.from_db_alias)
        assignment_group = self.get_or_create_assignment_group(assignment=assignment,
                                                               assignment_group_kwargs=assignment_group_kwargs,
                                                               db_alias=self.from_db_alias)
        user = self.get_or_create_user(user_kwargs=user_kwargs, db_alias=self.from_db_alias)
        related_student = self.get_or_create_related_student(user=user, period=period, db_alias=self.from_db_alias)
        self.get_or_create_candidate(assignment_group=assignment_group, related_student=related_student,
                                     candidate_kwargs=candidate_kwargs, db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_candidate=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(core_models.Candidate.objects.count(), 1)
        default_candidate = core_models.Candidate.objects.get()
        self.assertEqual(default_candidate.relatedstudent.user.shortname, 'default_user')
        self.assertEqual(default_candidate.relatedstudent.period.short_name, 'default_period')
        self.assertEqual(default_candidate.relatedstudent.period.parentnode.short_name,
                         'default_subject')
        self.assertEqual(default_candidate.assignment_group.name, 'default_group')
        self.assertEqual(default_candidate.assignment_group.parentnode.short_name, 'default_assignment')
        self.assertEqual(default_candidate.assignment_group.parentnode.parentnode.short_name, 'default_period')
        self.assertEqual(default_candidate.assignment_group.parentnode.parentnode.parentnode.short_name,
                         'default_subject')

        # Test migrate database
        self.assertEqual(core_models.Candidate.objects.using(self.from_db_alias).count(), 1)
        migrate_candidate = core_models.Candidate.objects.using(self.from_db_alias)\
            .select_related('assignment_group',
                            'assignment_group__parentnode',
                            'assignment_group__parentnode__parentnode',
                            'assignment_group__parentnode__parentnode__parentnode',
                            'relatedstudent',
                            'relatedstudent__user',
                            'relatedstudent__period',
                            'relatedstudent__period__parentnode')\
            .get()
        self.assertEqual(migrate_candidate.relatedstudent.user.shortname, 'migrate_user')
        self.assertEqual(migrate_candidate.relatedstudent.period.short_name, 'migrate_period')
        self.assertEqual(migrate_candidate.relatedstudent.period.parentnode.short_name,
                         'migrate_subject')
        self.assertEqual(migrate_candidate.assignment_group.name, 'migrate_group')
        self.assertEqual(migrate_candidate.assignment_group.parentnode.short_name, 'migrate_assignment')
        self.assertEqual(migrate_candidate.assignment_group.parentnode.parentnode.short_name,
                         'migrate_period')
        self.assertEqual(migrate_candidate.assignment_group.parentnode.parentnode.parentnode.short_name,
                         'migrate_subject')

    def test_import_single_candidate(self):
        # Default database data
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'},
            assignment_group_kwargs={'name': 'migrate_group'},
            user_kwargs={'shortname': 'migrate_user'})

        # Migrate database data
        self.__create_for_migrate_db()

        # Create TempMergeId for AssignmentGroup
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Candidate.objects.count(), 0)
        assignment_group_merger.CandidateMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Candidate.objects.count(), 1)
        self.assertEqual(core_models.Candidate.objects.get().assignment_group.name, 'migrate_group')
        self.assertEqual(core_models.Candidate.objects.get().relatedstudent.user.shortname, 'migrate_user')
        self.assertEqual(core_models.Candidate.objects.get().relatedstudent.period.short_name, 'migrate_period')

    def test_import_multiple_candidates_one_for_each_user_on_same_group(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'},
            'assignment_group_kwargs': {'name': 'migrate_group'}
        }
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Migrate database data
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user1'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user2'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user3'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user4'})

        # Create TempMergeId for AssignmentGroup
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Candidate.objects.count(), 0)
        assignment_group_merger.CandidateMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Candidate.objects.count(), 4)

        assignment_group = core_models.AssignmentGroup.objects.get()
        self.assertEqual(
            core_models.Candidate.objects.filter(
                assignment_group_id=assignment_group.id,
                relatedstudent__user__shortname='migrate_user1').count(), 1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                assignment_group_id=assignment_group.id,
                relatedstudent__user__shortname='migrate_user2').count(), 1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                assignment_group_id=assignment_group.id,
                relatedstudent__user__shortname='migrate_user3').count(), 1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                assignment_group_id=assignment_group.id,
                relatedstudent__user__shortname='migrate_user4').count(), 1)

    def test_import_multiple_candidates_on_multiple_assignment_groups(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'}
        }
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group1'},
                                     user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group2'},
                                     user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group3'},
                                     user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group4'},
                                     user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Migrate database data

        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group1'},
                                     user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group2'},
                                     user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group3'},
                                     user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group4'},
                                     user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Create TempMergeIds for AssignmentGroups
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group1').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group1').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group2').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group2').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group3').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group3').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group4').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group4').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Candidate.objects.count(), 0)
        assignment_group_merger.CandidateMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Candidate.objects.count(), 4)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                relatedstudent__user__shortname='migrate_user1',
                assignment_group__name='migrate_group1').count(),
            1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                relatedstudent__user__shortname='migrate_user2',
                assignment_group__name='migrate_group2').count(),
            1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                relatedstudent__user__shortname='migrate_user3',
                assignment_group__name='migrate_group3').count(),
            1)
        self.assertEqual(
            core_models.Candidate.objects.filter(
                relatedstudent__user__shortname='migrate_user4',
                assignment_group__name='migrate_group4').count(),
            1)


class TestExaminerMerger(MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, user_kwargs=None,
                                with_examiner=False, examiner_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment_group = self.get_or_create_assignment_group(assignment=assignment,
                                                               assignment_group_kwargs=assignment_group_kwargs)
        user = self.get_or_create_user(user_kwargs=user_kwargs)
        related_examiner = self.get_or_create_related_examiner(user=user, period=period)
        if with_examiner:
            self.get_or_create_examiner(assignment_group=assignment_group, related_examiner=related_examiner,
                                        examiner_kwargs=examiner_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, user_kwargs=None, examiner_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'migrate_group'}
        if not user_kwargs:
            user_kwargs = {'shortname': 'migrate_user'}
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs, db_alias=self.from_db_alias)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs, db_alias=self.from_db_alias)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs,
                                                   db_alias=self.from_db_alias)
        assignment_group = self.get_or_create_assignment_group(assignment=assignment,
                                                               assignment_group_kwargs=assignment_group_kwargs,
                                                               db_alias=self.from_db_alias)
        user = self.get_or_create_user(user_kwargs=user_kwargs, db_alias=self.from_db_alias)
        related_examiner = self.get_or_create_related_examiner(user=user, period=period, db_alias=self.from_db_alias)
        self.get_or_create_examiner(assignment_group=assignment_group, related_examiner=related_examiner,
                                    examiner_kwargs=examiner_kwargs, db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_examiner=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(core_models.Examiner.objects.count(), 1)
        default_examiner = core_models.Examiner.objects.get()
        self.assertEqual(default_examiner.relatedexaminer.user.shortname, 'default_user')
        self.assertEqual(default_examiner.relatedexaminer.period.short_name, 'default_period')
        self.assertEqual(default_examiner.relatedexaminer.period.parentnode.short_name,
                         'default_subject')
        self.assertEqual(default_examiner.assignmentgroup.name, 'default_group')
        self.assertEqual(default_examiner.assignmentgroup.parentnode.short_name, 'default_assignment')
        self.assertEqual(default_examiner.assignmentgroup.parentnode.parentnode.short_name, 'default_period')
        self.assertEqual(default_examiner.assignmentgroup.parentnode.parentnode.parentnode.short_name,
                         'default_subject')

        # Test migrate database
        self.assertEqual(core_models.Examiner.objects.using(self.from_db_alias).count(), 1)
        migrate_examiner = core_models.Examiner.objects.using(self.from_db_alias)\
            .select_related('assignmentgroup',
                            'assignmentgroup__parentnode',
                            'assignmentgroup__parentnode__parentnode',
                            'assignmentgroup__parentnode__parentnode__parentnode',
                            'relatedexaminer',
                            'relatedexaminer__user',
                            'relatedexaminer__period',
                            'relatedexaminer__period__parentnode')\
            .get()
        self.assertEqual(migrate_examiner.relatedexaminer.user.shortname, 'migrate_user')
        self.assertEqual(migrate_examiner.relatedexaminer.period.short_name, 'migrate_period')
        self.assertEqual(migrate_examiner.relatedexaminer.period.parentnode.short_name,
                         'migrate_subject')
        self.assertEqual(migrate_examiner.assignmentgroup.name, 'migrate_group')
        self.assertEqual(migrate_examiner.assignmentgroup.parentnode.short_name, 'migrate_assignment')
        self.assertEqual(migrate_examiner.assignmentgroup.parentnode.parentnode.short_name,
                         'migrate_period')
        self.assertEqual(migrate_examiner.assignmentgroup.parentnode.parentnode.parentnode.short_name,
                         'migrate_subject')

    def test_import_single_examiner(self):
        # Default database data
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'},
            assignment_group_kwargs={'name': 'migrate_group'},
            user_kwargs={'shortname': 'migrate_user'})

        # Migrate database data
        self.__create_for_migrate_db()

        # Create TempMergeId for AssignmentGroup
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Examiner.objects.count(), 0)
        assignment_group_merger.ExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Examiner.objects.count(), 1)
        self.assertEqual(core_models.Examiner.objects.get().assignmentgroup.name, 'migrate_group')
        self.assertEqual(core_models.Examiner.objects.get().relatedexaminer.user.shortname, 'migrate_user')
        self.assertEqual(core_models.Examiner.objects.get().relatedexaminer.period.short_name, 'migrate_period')

    def test_import_multiple_examiners_one_for_each_user_on_same_group(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'},
            'assignment_group_kwargs': {'name': 'migrate_group'}
        }
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_default_db(user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Migrate database data
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user1'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user2'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user3'})
        self.__create_for_migrate_db(user_kwargs={'shortname': 'migrate_user4'})

        # Create TempMergeId for AssignmentGroup
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Examiner.objects.count(), 0)
        assignment_group_merger.ExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Examiner.objects.count(), 4)

        assignment_group = core_models.AssignmentGroup.objects.get()
        self.assertEqual(
            core_models.Examiner.objects.filter(
                assignmentgroup_id=assignment_group.id,
                relatedexaminer__user__shortname='migrate_user1').count(), 1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                assignmentgroup_id=assignment_group.id,
                relatedexaminer__user__shortname='migrate_user2').count(), 1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                assignmentgroup_id=assignment_group.id,
                relatedexaminer__user__shortname='migrate_user3').count(), 1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                assignmentgroup_id=assignment_group.id,
                relatedexaminer__user__shortname='migrate_user4').count(), 1)

    def test_import_multiple_examiners_on_multiple_assignment_groups(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'}
        }
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group1'},
                                     user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group2'},
                                     user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group3'},
                                     user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_default_db(assignment_group_kwargs={'name': 'migrate_group4'},
                                     user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Migrate database data

        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group1'},
                                     user_kwargs={'shortname': 'migrate_user1'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group2'},
                                     user_kwargs={'shortname': 'migrate_user2'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group3'},
                                     user_kwargs={'shortname': 'migrate_user3'}, **default_db_kwarg_data)
        self.__create_for_migrate_db(assignment_group_kwargs={'name': 'migrate_group4'},
                                     user_kwargs={'shortname': 'migrate_user4'}, **default_db_kwarg_data)

        # Create TempMergeIds for AssignmentGroups
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group1').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group1').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group2').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group2').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group3').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group3').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group4').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group4').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(core_models.Examiner.objects.count(), 0)
        assignment_group_merger.ExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Examiner.objects.count(), 4)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                relatedexaminer__user__shortname='migrate_user1',
                assignmentgroup__name='migrate_group1').count(),
            1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                relatedexaminer__user__shortname='migrate_user2',
                assignmentgroup__name='migrate_group2').count(),
            1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                relatedexaminer__user__shortname='migrate_user3',
                assignmentgroup__name='migrate_group3').count(),
            1)
        self.assertEqual(
            core_models.Examiner.objects.filter(
                relatedexaminer__user__shortname='migrate_user4',
                assignmentgroup__name='migrate_group4').count(),
            1)
