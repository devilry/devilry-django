# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_comment', '0001_initial'),
        ('core', '0002_auto_20150915_1127'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.PositiveIntegerField()),
                ('created_datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('published_datetime', models.DateTimeField(null=True, blank=True)),
                ('deadline_datetime', models.DateTimeField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_feedbacksets', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('group', models.ForeignKey(to='core.AssignmentGroup', on_delete=models.CASCADE)),
                ('published_by', models.ForeignKey(related_name='published_feedbacksets', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='GroupComment',
            fields=[
                ('comment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='devilry_comment.Comment', on_delete=models.CASCADE)),
                ('instant_publish', models.BooleanField(default=False)),
                ('visible_for_students', models.BooleanField(default=False)),
                ('feedback_set', models.ForeignKey(to='devilry_group.FeedbackSet', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('devilry_comment.comment',),
        ),
        migrations.CreateModel(
            name='ImageAnnotationComment',
            fields=[
                ('comment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='devilry_comment.Comment', on_delete=models.CASCADE)),
                ('instant_publish', models.BooleanField(default=False)),
                ('visible_for_students', models.BooleanField(default=False)),
                ('x_coordinate', models.PositiveIntegerField()),
                ('y_coordinate', models.PositiveIntegerField()),
                ('feedback_set', models.ForeignKey(to='devilry_group.FeedbackSet', on_delete=models.CASCADE)),
                ('image', models.ForeignKey(to='devilry_comment.CommentFileImage', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('devilry_comment.comment',),
        ),
    ]
