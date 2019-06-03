# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeadlineTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PeriodTag',
            fields=[
                ('period', models.OneToOneField(primary_key=True, serialize=False, to='core.Period', on_delete=models.CASCADE)),
                ('deadlinetag', models.ForeignKey(to='devilry_qualifiesforexam.DeadlineTag', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='QualifiesForFinalExam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qualifies', models.NullBooleanField()),
                ('relatedstudent', models.ForeignKey(to='core.RelatedStudent', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SlugField(max_length=30, choices=[('ready', 'Ready for export'), ('almostready', 'Most students are ready for export'), ('notready', 'Not ready for export (retracted)')])),
                ('createtime', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True)),
                ('plugin', models.CharField(max_length=500, null=True, blank=True)),
                ('exported_timestamp', models.DateTimeField(null=True, blank=True)),
                ('period', models.ForeignKey(related_name='qualifiedforexams_status', to='core.Period', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-createtime'],
                'verbose_name': 'Qualified for final exam status',
                'verbose_name_plural': 'Qualified for final exam statuses',
            },
        ),
        migrations.AddField(
            model_name='qualifiesforfinalexam',
            name='status',
            field=models.ForeignKey(related_name='students', to='devilry_qualifiesforexam.Status', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='qualifiesforfinalexam',
            unique_together=set([('relatedstudent', 'status')]),
        ),
    ]
