# -*- coding: utf-8 -*-


from django.db import migrations

def examiner_relatedexaminer_replaces_user_field(apps, schema_editor):
    examiner_model = apps.get_model('core', 'Examiner')
    relatedexaminer_model = apps.get_model('core', 'RelatedExaminer')
    for examiner in examiner_model.objects.all().select_related('assignmentgroup__parentnode__parentnode'):
        period = examiner.assignmentgroup.parentnode.parentnode
        relatedexaminer, created = relatedexaminer_model.objects.get_or_create(
            user=examiner.user,
            period=period
        )
        if created:
            relatedexaminer.active = False
            relatedexaminer.save()
        examiner.relatedexaminer = relatedexaminer
        examiner.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_relatedexaminer_active'),
    ]

    operations = [
        migrations.RunPython(examiner_relatedexaminer_replaces_user_field)
    ]
