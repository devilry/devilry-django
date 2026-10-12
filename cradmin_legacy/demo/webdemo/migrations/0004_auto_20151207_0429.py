from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webdemo', '0003_auto_20151207_0351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='subscribers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, verbose_name='Subscribed users'),
            preserve_default=True,
        ),
    ]
