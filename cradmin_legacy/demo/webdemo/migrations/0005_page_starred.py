from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webdemo', '0004_auto_20151207_0429'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='starred',
            field=models.CharField(max_length=3, default='no', choices=[('yes', 'Yes'), ('no', 'No')]),
        ),
    ]
