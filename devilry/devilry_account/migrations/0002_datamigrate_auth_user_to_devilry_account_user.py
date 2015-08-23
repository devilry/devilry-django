# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def datamigrate_auth_user_to_devilry_account_user(apps, schema_editor):
    old_user_model = apps.get_model("auth", "User")
    old_profile_model = apps.get_model("core", "DevilryUserProfile")
    new_user_model = apps.get_model("devilry_account", "User")
    useremail_model = apps.get_model("devilry_account", "UserEmail")
    username_model = apps.get_model("devilry_account", "UserName")
    for old_user in old_user_model.objects.all():
        old_profile = old_profile_model.objects.get(user_id=old_user.id)
        new_user = new_user_model(
            id=old_user.id,
            shortname=old_user.username,
            is_superuser=old_user.is_superuser,
            last_login=old_user.last_login,
            fullname=old_profile.full_name or '',
            languagecode=old_profile.languagecode or '',
            password=old_user.password
        )
        if old_profile.full_name:
            new_user.lastname = old_profile.full_name.split()[-1]
        new_user.save()

        username = username_model(
            user=new_user,
            username=old_user.username, is_primary=True)
        username.save()
        if old_user.email:
            useremail = useremail_model(
                user=new_user,
                email=old_user.email, use_for_notifications=True, is_primary=True)
            useremail.save()


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_account', '0001_initial'),
        ('auth', '0001_initial'),
        ('core', '0007_auto_20150601_2125'),
    ]

    operations = [
        migrations.RunPython(datamigrate_auth_user_to_devilry_account_user),
    ]
