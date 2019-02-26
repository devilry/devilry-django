# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-02 10:35


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0041_auto_20180220_0651'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateAssignmentGroupHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_add', models.BooleanField()),
                ('assignment_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.AssignmentGroup')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Candidate group history',
                'verbose_name_plural': 'Candidate group histories',
            },
        ),
        migrations.CreateModel(
            name='ExaminerAssignmentGroupHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_add', models.BooleanField()),
                ('assignment_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.AssignmentGroup')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Examiner assignment group history',
                'verbose_name_plural': 'Examiner assignment group histories',
            },
        ),
    ]
