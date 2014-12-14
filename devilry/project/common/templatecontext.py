from django.conf import settings

from devilry.devilry_settings.views import urlsetting_or_unsetview


def template_variables(request):
    return {
        'DEVILRY_STATIC_URL': settings.DEVILRY_STATIC_URL,
        'DEVILRY_URLPATH_PREFIX': settings.DEVILRY_URLPATH_PREFIX,
        'DEVILRY_LOGOUT_URL': settings.DEVILRY_LOGOUT_URL,
        'session': request.session,
        'DEVILRY_EXTJS_URL': settings.DEVILRY_EXTJS_URL,
        'DEVILRY_MATHJAX_URL': settings.DEVILRY_MATHJAX_URL,
        'DEVILRY_HELP_URL': settings.DEVILRY_HELP_URL,
        'DEVILRY_SYSTEM_ADMIN_EMAIL': settings.DEVILRY_SYSTEM_ADMIN_EMAIL,
        'DEVILRY_SORT_FULL_NAME_BY_LASTNAME': settings.DEVILRY_SORT_FULL_NAME_BY_LASTNAME,
        'DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD': settings.DEFAULT_DEADLINE_HANDLING_METHOD,
        'DEVILRY_ENABLE_MATHJAX': settings.DEVILRY_ENABLE_MATHJAX,
        'DEVILRY_SYNCSYSTEM': settings.DEVILRY_SYNCSYSTEM,
        'DEVILRY_LACKING_PERMISSIONS_URL': urlsetting_or_unsetview('DEVILRY_LACKING_PERMISSIONS_URL'),
    }
