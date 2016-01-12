# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def candidate_relatedstudent_replaces_student_field(apps, schema_editor):
    candidate_model = apps.get_model('core', 'Candidate')
    relatedstudent_model = apps.get_model('core', 'RelatedStudent')
    for candidate in candidate_model.objects.all().select_related('assignment_group__parentnode__parentnode'):
        period = candidate.assignment_group.parentnode.parentnode
        relatedstudent, created = relatedstudent_model.objects.get_or_create(
            user=candidate.old_reference_not_in_use_student,
            period=period
        )
        if created:
            relatedstudent.active = False
            relatedstudent.save()
        candidate.relatedstudent = relatedstudent
        candidate.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160112_1831'),
    ]

    operations = [
        migrations.RunPython(candidate_relatedstudent_replaces_student_field)
    ]
