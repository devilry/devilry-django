from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required
def missing_setting(request, setting):
    message = """
You have been redirected to this view because your local Devilry system administrator
have not set the <strong>{setting}</strong>-setting. Please tell them to set it.""".format(setting=setting)
    return HttpResponse('<html><body>{message}</body></html>'.format(message=message))


def urlsetting_or_unsetview(settingname):
    setting = getattr(settings, settingname, None)
    if setting:
        return setting
    else:
        return reverse('devilry_settings_missing_setting', args=(settingname,))
