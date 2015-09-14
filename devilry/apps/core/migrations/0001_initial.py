# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
import devilry.apps.core.models.abstract_is_examiner
import devilry.apps.core.models.abstract_is_candidate
import devilry.apps.core.models.custom_db_fields
import devilry.apps.core.models.static_feedback
import devilry.apps.core.models.basenode
import devilry.apps.core.models.model_utils
import django.db.models.deletion
from django.conf import settings
import devilry.apps.core.models.abstract_is_admin


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). This is used when the the regular name takes to much space. Be VERY careful about changing the short name - it is typically used as an identifier when importing and exporting data from Devilry.', max_length=20, verbose_name='Short name')),
                ('long_name', devilry.apps.core.models.custom_db_fields.LongNameField(max_length=100, verbose_name=b'Name', db_index=True)),
                ('publishing_time', models.DateTimeField(help_text='The time when the assignment is to be published (visible to students and examiners).', verbose_name='Publishing time')),
                ('anonymous', models.BooleanField(default=False, help_text='On anonymous assignments, examiners and students can NOT see each other and they can NOT communicate. If an assignment is anonymous, examiners see candidate-id instead of any personal information about the students. This means that anonymous assignments is perfect for exams, and for assignments where you do not want prior experiences with a student to affect results.', verbose_name='Anonymous?')),
                ('students_can_see_points', models.BooleanField(default=True, verbose_name=b'Students can see points')),
                ('delivery_types', models.PositiveIntegerField(default=0, help_text=b'This option controls what types of deliveries this assignment accepts. See the Delivery documentation for more info.', choices=[(0, b'Electronic'), (1, b'Non electronic'), (2, b'Alias')])),
                ('deadline_handling', models.PositiveIntegerField(default=0, help_text='With HARD deadlines, students will be unable to make deliveries when a deadline has expired. With SOFT deadlines students will be able to make deliveries after the deadline has expired. All deliveries after their deadline are clearly highligted. NOTE: Devilry is designed from the bottom up to gracefully handle SOFT deadlines. Students have to perform an extra confirm-step when adding deliveries after their active deadline, and assignments where the deadline has expired is clearly marked for both students and examiners.', verbose_name='Deadline handling', choices=[(0, 'Soft deadlines'), (1, 'Hard deadlines')])),
                ('scale_points_percent', models.PositiveIntegerField(default=100, help_text=b'Percent to scale points on this assignment by for period overviews. The default is 100, which means no change to the points.')),
                ('first_deadline', models.DateTimeField(null=True, blank=True)),
                ('max_points', models.PositiveIntegerField(default=1, help_text='Specify the maximum number of points possible for this assignment.', null=True, verbose_name='Maximum points', blank=True)),
                ('passing_grade_min_points', models.PositiveIntegerField(default=1, null=True, verbose_name='Minumum number of points required to pass', blank=True)),
                ('points_to_grade_mapper', models.CharField(default=b'passed-failed', max_length=25, null=True, blank=True, choices=[(b'passed-failed', 'As passed or failed'), (b'raw-points', 'As points'), (b'custom-table', 'As a text looked up in a custom table')])),
                ('grading_system_plugin_id', models.CharField(default=b'devilry_gradingsystemplugin_approved', max_length=300, null=True, blank=True)),
                ('students_can_create_groups', models.BooleanField(default=False, help_text='Select this if students should be allowed to join/leave groups. Even if this is not selected, you can still organize your students in groups manually.', verbose_name='Students can create project groups?')),
                ('students_can_not_create_groups_after', models.DateTimeField(default=None, help_text='Students can not create project groups after this time. Ignored if "Students can create project groups" is not selected.', null=True, verbose_name='Students can not create project groups after', blank=True)),
                ('feedback_workflow', models.CharField(default=b'', max_length=50, verbose_name='Feedback workflow', blank=True, choices=[(b'', 'Simple - Examiners write feedback, and publish it whenever they want. Does not handle coordination of multiple examiners at all.'), (b'trusted-cooperative-feedback-editing', 'Trusted cooperative feedback editing - Examiners can only save feedback drafts. Examiners share the same feedback drafts, which means that one examiner can start writing feedback and another can continue. When an administrator is notified by their examiners that they have finished correcting, they can publish the drafts via the administrator UI. If you want one examiner to do the bulk of the work, and just let another examiner read it over and adjust the feedback, make the first examiner the only examiner, and reassign the students to the other examiner when the first examiner is done.')])),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name=b'Administrators', blank=True)),
            ],
            options={
                'ordering': ['short_name'],
            },
            bases=(models.Model, devilry.apps.core.models.basenode.BaseNode, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate),
        ),
        migrations.CreateModel(
            name='AssignmentGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'An optional name for the group. Typically used a project name on project assignments.', max_length=30, null=True, blank=True)),
                ('is_open', models.BooleanField(default=True, help_text=b'If this is checked, the group can add deliveries.')),
                ('etag', models.DateTimeField(auto_now_add=True)),
                ('delivery_status', models.CharField(blank=True, max_length=30, null=True, help_text=b'The delivery_status of a group', choices=[(b'no-deadlines', 'No deadlines'), (b'corrected', 'Corrected'), (b'closed-without-feedback', 'Closed without feedback'), (b'waiting-for-something', 'Waiting for something')])),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('copied_from', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.AssignmentGroup', null=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.model_utils.Etag),
        ),
        migrations.CreateModel(
            name='AssignmentGroupTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.SlugField(help_text=b'A tag can contain a-z, A-Z, 0-9 and "_".', max_length=20)),
                ('assignment_group', models.ForeignKey(related_name='tags', to='core.AssignmentGroup')),
            ],
            options={
                'ordering': ['tag'],
            },
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('candidate_id', models.CharField(help_text=b'An optional candidate id. This can be anything as long as it is less than 30 characters. Used to show the user on anonymous assignmens.', max_length=30, null=True, blank=True)),
                ('automatic_anonymous_id', models.CharField(default=b'', help_text=b'An automatically generated anonymous ID.', max_length=255, blank=True)),
                ('assignment_group', models.ForeignKey(related_name='candidates', to='core.AssignmentGroup')),
                ('student', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Deadline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deadline', models.DateTimeField(help_text=b'The time of the deadline.')),
                ('text', models.TextField(help_text=b'An optional text to show to students and examiners.', null=True, blank=True)),
                ('deliveries_available_before_deadline', models.BooleanField(default=False, help_text=b'Should deliveries on this deadline be available to examiners before thedeadline expires? This is set by students.')),
                ('why_created', models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(None, 'Unknown.'), (b'examiner-gave-another-chance', 'Examiner gave the student another chance.')])),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('assignment_group', models.ForeignKey(related_name='deadlines', to='core.AssignmentGroup')),
            ],
            options={
                'ordering': ['-deadline'],
                'verbose_name': 'Deadline',
                'verbose_name_plural': 'Deadlines',
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate),
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('delivery_type', models.PositiveIntegerField(default=0, help_text=b'0: Electronic delivery, 1: Non-electronic delivery, 2: Alias delivery. Default: 0.', verbose_name=b'Type of delivery')),
                ('time_of_delivery', models.DateTimeField(default=datetime.datetime.now, help_text=b'Holds the date and time the Delivery was uploaded.', verbose_name='Time of delivery')),
                ('number', models.PositiveIntegerField(help_text=b'The delivery-number within this assignment-group. This number is automatically incremented within each AssignmentGroup, starting from 1. Always unique within the assignment-group.')),
                ('successful', models.BooleanField(default=True, help_text=b'Has the delivery and all its files been uploaded successfully?')),
                ('alias_delivery', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Delivery', help_text=b'Links to another delivery. Used when delivery_type is Alias.', null=True)),
                ('copy_of', models.ForeignKey(related_name='copies', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Delivery', help_text=b'Link to a delivery that this delivery is a copy of. This is set by the copy-method.', null=True)),
                ('deadline', models.ForeignKey(related_name='deliveries', verbose_name='Deadline', to='core.Deadline')),
                ('delivered_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Candidate', help_text=b'The candidate that delivered this delivery. If this is None, the delivery was made by an administrator for a student.', null=True)),
            ],
            options={
                'ordering': ['-time_of_delivery'],
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer),
        ),
        migrations.CreateModel(
            name='DevilryUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=300, null=True, blank=True)),
                ('languagecode', models.CharField(max_length=100, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Examiner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('automatic_anonymous_id', models.CharField(default=b'', help_text=b'An automatically generated anonymous ID.', max_length=255, blank=True)),
                ('assignmentgroup', models.ForeignKey(related_name='examiners', to='core.AssignmentGroup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_assignmentgroup_examiners',
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin),
        ),
        migrations.CreateModel(
            name='FileMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(help_text=b'Name of the file.', max_length=255)),
                ('size', models.IntegerField(help_text=b'Size of the file in bytes.')),
                ('delivery', models.ForeignKey(related_name='filemetas', to='core.Delivery')),
            ],
            options={
                'ordering': ['filename'],
                'verbose_name': 'FileMeta',
                'verbose_name_plural': 'FileMetas',
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate),
        ),
        migrations.CreateModel(
            name='GroupInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent_datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('accepted', models.NullBooleanField(default=None)),
                ('responded_datetime', models.DateTimeField(default=None, null=True, blank=True)),
                ('group', models.ForeignKey(to='core.AssignmentGroup')),
                ('sent_by', models.ForeignKey(related_name='groupinvite_sent_by_set', to=settings.AUTH_USER_MODEL)),
                ('sent_to', models.ForeignKey(related_name='groupinvite_sent_to_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). This is used when the the regular name takes to much space. Be VERY careful about changing the short name - it is typically used as an identifier when importing and exporting data from Devilry.', max_length=20, verbose_name='Short name')),
                ('long_name', devilry.apps.core.models.custom_db_fields.LongNameField(max_length=100, verbose_name=b'Name', db_index=True)),
                ('etag', models.DateTimeField(auto_now=True)),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('parentnode', models.ForeignKey(related_name='child_nodes', blank=True, to='core.Node', null=True)),
            ],
            options={
                'ordering': ['short_name'],
            },
            bases=(models.Model, devilry.apps.core.models.basenode.BaseNode, devilry.apps.core.models.model_utils.Etag),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). This is used when the the regular name takes to much space. Be VERY careful about changing the short name - it is typically used as an identifier when importing and exporting data from Devilry.', max_length=20, verbose_name='Short name')),
                ('long_name', devilry.apps.core.models.custom_db_fields.LongNameField(max_length=100, verbose_name=b'Name', db_index=True)),
                ('start_time', models.DateTimeField(help_text=b'Start time and end time defines when the period is active.')),
                ('end_time', models.DateTimeField(help_text=b'Start time and end time defines when the period is active.')),
                ('etag', models.DateTimeField(auto_now_add=True)),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['short_name'],
            },
            bases=(models.Model, devilry.apps.core.models.basenode.BaseNode, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate, devilry.apps.core.models.model_utils.Etag),
        ),
        migrations.CreateModel(
            name='PeriodApplicationKeyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application', models.CharField(help_text=b'Application identifier. Max 300 chars.', max_length=300, db_index=True)),
                ('key', models.CharField(help_text=b'Key. Max 300 chars.', max_length=300, db_index=True)),
                ('value', models.TextField(help_text=b'Value.', null=True, db_index=True, blank=True)),
                ('period', models.ForeignKey(help_text=b'The period where this metadata belongs.', to='core.Period')),
            ],
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin),
        ),
        migrations.CreateModel(
            name='PointRangeToGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minimum_points', models.PositiveIntegerField()),
                ('maximum_points', models.PositiveIntegerField()),
                ('grade', models.CharField(max_length=12)),
            ],
            options={
                'ordering': ['minimum_points'],
            },
        ),
        migrations.CreateModel(
            name='PointToGradeMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invalid', models.BooleanField(default=True)),
                ('assignment', models.OneToOneField(to='core.Assignment')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedExaminer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.TextField(help_text=b'Comma-separated list of tags. Each tag is a word with the following letters allowed: a-z, 0-9, ``_`` and ``-``. Each word is separated by a comma, and no whitespace.', null=True, blank=True)),
                ('period', models.ForeignKey(verbose_name=b'Period', to='core.Period', help_text=b'The period.')),
                ('user', models.ForeignKey(help_text=b'The related user.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin),
        ),
        migrations.CreateModel(
            name='RelatedExaminerSyncSystemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=15, db_index=True)),
                ('relatedexaminer', models.ForeignKey(to='core.RelatedExaminer')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedStudent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.TextField(help_text=b'Comma-separated list of tags. Each tag is a word with the following letters allowed: a-z, 0-9, ``_`` and ``-``. Each word is separated by a comma, and no whitespace.', null=True, blank=True)),
                ('candidate_id', models.CharField(max_length=30, null=True, blank=True)),
                ('automatic_anonymous_id', models.CharField(default=b'', max_length=255, editable=False, blank=True)),
                ('period', models.ForeignKey(verbose_name=b'Period', to='core.Period', help_text=b'The period.')),
                ('user', models.ForeignKey(help_text=b'The related user.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin),
        ),
        migrations.CreateModel(
            name='RelatedStudentKeyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application', models.CharField(help_text=b'Application identifier. Max 300 chars.', max_length=300, db_index=True)),
                ('key', models.CharField(help_text=b'Key. Max 300 chars.', max_length=300, db_index=True)),
                ('value', models.TextField(help_text=b'Value.', null=True, db_index=True, blank=True)),
                ('student_can_read', models.BooleanField(default=False, help_text=b'Specifies if a student can read the value or not.')),
                ('relatedstudent', models.ForeignKey(to='core.RelatedStudent')),
            ],
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin),
        ),
        migrations.CreateModel(
            name='RelatedStudentSyncSystemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=15, db_index=True)),
                ('relatedstudent', models.ForeignKey(to='core.RelatedStudent')),
            ],
        ),
        migrations.CreateModel(
            name='StaticFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rendered_view', models.TextField(help_text=b'A rendered HTML version of the feedback, containing whatever the grade-editor chose to dump in this field.', blank=True)),
                ('grade', models.CharField(help_text=b'The rendered grade, such as "A" or "approved".', max_length=12)),
                ('points', models.PositiveIntegerField(help_text=b'Number of points given on this feedback.')),
                ('is_passing_grade', models.BooleanField(default=False, help_text=b'Is this a passing grade?')),
                ('save_timestamp', models.DateTimeField(help_text=b'Time when this feedback was saved. Since StaticFeedback is immutable, this never changes.', null=True, blank=True)),
                ('delivery', models.ForeignKey(related_name='feedbacks', to='core.Delivery')),
                ('saved_by', models.ForeignKey(help_text=b'The user (examiner) who saved this feedback', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-save_timestamp'],
                'verbose_name': 'Static feedback',
                'verbose_name_plural': 'Static feedbacks',
            },
            bases=(models.Model, devilry.apps.core.models.abstract_is_admin.AbstractIsAdmin, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate),
        ),
        migrations.CreateModel(
            name='StaticFeedbackFileAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.TextField()),
                ('file', models.FileField(upload_to=devilry.apps.core.models.static_feedback.staticfeedback_fileattachment_upload_to)),
                ('staticfeedback', models.ForeignKey(related_name='files', to='core.StaticFeedback')),
            ],
            options={
                'ordering': ['filename'],
                'verbose_name': 'Static feedback file attachment',
                'verbose_name_plural': 'Static feedback file attachments',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', devilry.apps.core.models.custom_db_fields.ShortNameField(help_text='A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ("_") and hyphen ("-"). This is used when the the regular name takes to much space. Be VERY careful about changing the short name - it is typically used as an identifier when importing and exporting data from Devilry.', unique=True, max_length=20, verbose_name='Short name')),
                ('long_name', devilry.apps.core.models.custom_db_fields.LongNameField(max_length=100, verbose_name=b'Name', db_index=True)),
                ('etag', models.DateTimeField(auto_now_add=True)),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('parentnode', models.ForeignKey(related_name='subjects', to='core.Node')),
            ],
            options={
                'ordering': ['short_name'],
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
            bases=(models.Model, devilry.apps.core.models.basenode.BaseNode, devilry.apps.core.models.abstract_is_examiner.AbstractIsExaminer, devilry.apps.core.models.abstract_is_candidate.AbstractIsCandidate, devilry.apps.core.models.model_utils.Etag),
        ),
        migrations.AddField(
            model_name='pointrangetograde',
            name='point_to_grade_map',
            field=models.ForeignKey(to='core.PointToGradeMap'),
        ),
        migrations.AddField(
            model_name='period',
            name='parentnode',
            field=models.ForeignKey(related_name='periods', verbose_name=b'Subject', to='core.Subject'),
        ),
        migrations.AddField(
            model_name='delivery',
            name='last_feedback',
            field=models.OneToOneField(related_name='latest_feedback_for_delivery', null=True, blank=True, to='core.StaticFeedback'),
        ),
        migrations.AddField(
            model_name='assignmentgroup',
            name='feedback',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.StaticFeedback'),
        ),
        migrations.AddField(
            model_name='assignmentgroup',
            name='last_deadline',
            field=models.OneToOneField(related_name='last_deadline_for_group', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Deadline'),
        ),
        migrations.AddField(
            model_name='assignmentgroup',
            name='parentnode',
            field=models.ForeignKey(related_name='assignmentgroups', to='core.Assignment'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='parentnode',
            field=models.ForeignKey(related_name='assignments', verbose_name=b'Period', to='core.Period'),
        ),
        migrations.AlterUniqueTogether(
            name='relatedstudentsyncsystemtag',
            unique_together=set([('relatedstudent', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='relatedstudentkeyvalue',
            unique_together=set([('relatedstudent', 'application', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='relatedstudent',
            unique_together=set([('period', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='relatedexaminersyncsystemtag',
            unique_together=set([('relatedexaminer', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='relatedexaminer',
            unique_together=set([('period', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='pointrangetograde',
            unique_together=set([('point_to_grade_map', 'grade')]),
        ),
        migrations.AlterUniqueTogether(
            name='periodapplicationkeyvalue',
            unique_together=set([('period', 'application', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('short_name', 'parentnode')]),
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together=set([('short_name', 'parentnode')]),
        ),
        migrations.AlterUniqueTogether(
            name='filemeta',
            unique_together=set([('delivery', 'filename')]),
        ),
        migrations.AlterUniqueTogether(
            name='examiner',
            unique_together=set([('user', 'assignmentgroup')]),
        ),
        migrations.AlterUniqueTogether(
            name='assignmentgrouptag',
            unique_together=set([('assignment_group', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together=set([('short_name', 'parentnode')]),
        ),
    ]
