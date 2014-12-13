from json import dumps
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import devilry


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
        return reverse(missing_setting, args=(settingname,))


@login_required
def settings_view(request):
    s = {'DEVILRY_STATIC_URL': settings.DEVILRY_STATIC_URL,
         'DEVILRY_SUPERUSERPANEL_URL': settings.DEVILRY_URLPATH_PREFIX + '/superuser/',
         'DEVILRY_URLPATH_PREFIX': settings.DEVILRY_URLPATH_PREFIX,
         'DEVILRY_LOGOUT_URL': settings.DEVILRY_LOGOUT_URL,
         'DEVILRY_EXTJS_URL': settings.DEVILRY_EXTJS_URL,
         'DEVILRY_MATHJAX_URL': settings.DEVILRY_MATHJAX_URL,
         'DEVILRY_LACKING_PERMISSIONS_URL': urlsetting_or_unsetview('DEVILRY_LACKING_PERMISSIONS_URL'),
         'DEVILRY_NOT_RELATEDSTUDENT_ON_PERIOD_URL': urlsetting_or_unsetview('DEVILRY_NOT_RELATEDSTUDENT_ON_PERIOD_URL'),
         'DEVILRY_WRONG_USERINFO_URL': urlsetting_or_unsetview('DEVILRY_WRONG_USERINFO_URL'),
         'DEVILRY_HELP_URL': settings.DEVILRY_HELP_URL,
         'DEVILRY_SYSTEM_ADMIN_EMAIL': settings.DEVILRY_SYSTEM_ADMIN_EMAIL,
         'DEVILRY_SORT_FULL_NAME_BY_LASTNAME': settings.DEVILRY_SORT_FULL_NAME_BY_LASTNAME,
         'DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD': settings.DEFAULT_DEADLINE_HANDLING_METHOD,
         'DEVILRY_ENABLE_MATHJAX': settings.DEVILRY_ENABLE_MATHJAX,
         'DEVILRY_VERSION': devilry.__version__,
         'DEVILRY_SYNCSYSTEM': settings.DEVILRY_SYNCSYSTEM}
    settings_json = dumps(s, indent=4)
    # NOTE: Defining this as ``window.DevilrySettings``, and not as ``var
    #       DevilrySettings``, makes it a global to all javascript in the window.
    #       See: https://developer.mozilla.org/en/JavaScript/Guide/Values,_Variables,_and_Literals#Global_variables
    js = 'window.DevilrySettings = {settings_json};'.format(settings_json=settings_json)
    return HttpResponse(js, content_type="application/javascript")
