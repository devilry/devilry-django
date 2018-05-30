from django.conf import settings
from django.templatetags.static import static
from django.utils import translation

import devilry

from devilry.devilry_settings.views import urlsetting_or_unsetview


def template_variables(request):
    template_variables_dict = {
        'DEVILRY_VERSION': devilry.__version__,
        'DEVILRY_STATIC_URL': settings.DEVILRY_STATIC_URL,
        'DEVILRY_URLPATH_PREFIX': settings.DEVILRY_URLPATH_PREFIX,
        'DEVILRY_LOGOUT_URL': settings.DEVILRY_LOGOUT_URL,
        'DEVILRY_THEME3_JAVASCRIPT_URL': '{static_url}/devilry_theme3/{theme3_version}/scripts/devilry_all.js'.format(
            static_url=settings.DEVILRY_STATIC_URL,
            theme3_version=devilry.__version__
        ),
        'session': request.session,
        'DEVILRY_MATHJAX_URL': settings.DEVILRY_MATHJAX_URL,
        'DEVILRY_HELP_URL': settings.DEVILRY_HELP_URL,
        'DEVILRY_CHANGELOG_URL': settings.DEVILRY_CHANGELOG_URL,
        'DEVILRY_SYSTEM_ADMIN_EMAIL': settings.DEVILRY_SYSTEM_ADMIN_EMAIL,
        'DEVILRY_DEFAULT_DEADLINE_HANDLING_METHOD': settings.DEFAULT_DEADLINE_HANDLING_METHOD,
        'DEVILRY_ENABLE_MATHJAX': settings.DEVILRY_ENABLE_MATHJAX,
        'DEVILRY_SYNCSYSTEM': settings.DEVILRY_SYNCSYSTEM,
        'DEVILRY_LACKING_PERMISSIONS_URL': urlsetting_or_unsetview('DEVILRY_LACKING_PERMISSIONS_URL'),
        'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND': getattr(settings, 'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND', False),
        'DJANGO_CRADMIN_FORGOTPASSWORD_URL': getattr(settings, 'DJANGO_CRADMIN_FORGOTPASSWORD_URL', None),
        'DEVILRY_FRONTPAGE_HEADER_INCLUDE_TEMPLATE': settings.DEVILRY_FRONTPAGE_HEADER_INCLUDE_TEMPLATE,
        'DEVILRY_FRONTPAGE_FOOTER_INCLUDE_TEMPLATE': settings.DEVILRY_FRONTPAGE_FOOTER_INCLUDE_TEMPLATE,
        'DEVILRY_HELP_PAGE_HEADER_INCLUDE_TEMPLATE': settings.DEVILRY_HELP_PAGE_HEADER_INCLUDE_TEMPLATE,
        'DEVILRY_HELP_PAGE_FOOTER_INCLUDE_TEMPLATE': settings.DEVILRY_HELP_PAGE_FOOTER_INCLUDE_TEMPLATE,
        'DEVILRY_PROFILEPAGE_HEADER_INCLUDE_TEMPLATE': settings.DEVILRY_PROFILEPAGE_HEADER_INCLUDE_TEMPLATE,
        'DEVILRY_PROFILEPAGE_FOOTER_INCLUDE_TEMPLATE': settings.DEVILRY_PROFILEPAGE_FOOTER_INCLUDE_TEMPLATE,
        'DEVILRY_ENABLE_REALTIME_ZIPFILE_CREATION': settings.DEVILRY_ENABLE_REALTIME_ZIPFILE_CREATION,
        'DEVILRY_THEME3_DIST_PATH': static('devilry_theme3/{}/'.format(devilry.__version__)),
        'DEVILRY_BRANDING_FAV_ICON_PATH': settings.DEVILRY_BRANDING_FAV_ICON_PATH
    }
    language_code = translation.get_language()
    if language_code != 'en':
        # We don't need to set the default translatiion
        template_variables_dict['DJANGO_CRADMIN_MOMENTJS_LOCALE'] = language_code
    return template_variables_dict
