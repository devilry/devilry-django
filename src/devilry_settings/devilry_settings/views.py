from json import dumps
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required


@login_required
def settings_view(request):
    s = {'DEVILRY_STATIC_URL': settings.DEVILRY_STATIC_URL,
         'DEVILRY_URLPATH_PREFIX': settings.DEVILRY_URLPATH_PREFIX,
         'DEVILRY_LOGOUT_URL': settings.DEVILRY_LOGOUT_URL,
         'DEVILRY_THEME_URL': settings.DEVILRY_THEME_URL,
         'DEVILRY_EXTJS_URL': settings.DEVILRY_EXTJS_URL,
         'DEVILRY_MATHJAX_URL': settings.DEVILRY_MATHJAX_URL,
         'DEVILRY_HELP_URL': settings.DEVILRY_HELP_URL,
         'DEVILRY_SYSTEM_ADMIN_EMAIL': settings.DEVILRY_SYSTEM_ADMIN_EMAIL,
         'DEVILRY_STUDENT_NO_PERMISSION_MSG': settings.DEVILRY_STUDENT_NO_PERMISSION_MSG,
         'DEVILRY_EXAMINER_NO_PERMISSION_MSG': settings.DEVILRY_EXAMINER_NO_PERMISSION_MSG,
         'DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG': settings.DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG,
         'DEVILRY_SORT_FULL_NAME_BY_LASTNAME': settings.DEVILRY_SORT_FULL_NAME_BY_LASTNAME,
         'DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD': settings.DEFAULT_DEADLINE_HANDLING_METHOD,
         'DEVILRY_SYNCSYSTEM': settings.DEVILRY_SYNCSYSTEM}
    settings_json = dumps(s, indent=4)
    # NOTE: Defining this as ``window.DevilrySettings``, and not as ``var
    #       DevilrySettings``, makes it a global to all javascript in the window.
    #       See: https://developer.mozilla.org/en/JavaScript/Guide/Values,_Variables,_and_Literals#Global_variables
    js = 'window.DevilrySettings = {settings_json};'.format(settings_json=settings_json)
    return HttpResponse(js, content_type="application/javascript")
