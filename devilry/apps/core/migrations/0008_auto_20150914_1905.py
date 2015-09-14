# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150601_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedExaminerSyncSystemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=15, db_index=True)),
                ('relatedexaminer', models.ForeignKey(to='core.RelatedExaminer')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedStudentSyncSystemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=15, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='assignmentgroup',
            name='copied_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.AssignmentGroup', null=True),
        ),
        migrations.AddField(
            model_name='assignmentgroup',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='automatic_anonymous_id',
            field=models.CharField(default=b'', help_text=b'An automatically generated anonymous ID.', max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='examiner',
            name='automatic_anonymous_id',
            field=models.CharField(default=b'', help_text=b'An automatically generated anonymous ID.', max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='relatedstudent',
            name='automatic_anonymous_id',
            field=models.CharField(default=b'', max_length=255, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='relatedstudent',
            name='candidate_id',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='relatedstudentsyncsystemtag',
            name='relatedstudent',
            field=models.ForeignKey(to='core.RelatedStudent'),
        ),
        migrations.AlterUniqueTogether(
            name='relatedstudentsyncsystemtag',
            unique_together=set([('relatedstudent', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='relatedexaminersyncsystemtag',
            unique_together=set([('relatedexaminer', 'tag')]),
        ),
    ]
