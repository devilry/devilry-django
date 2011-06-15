from django.conf import settings

from ..core.models import AssignmentGroup


def template_variables(request):
    return {
        'DEVILRY_JQUERY_UI_THEME': settings.DEVILRY_JQUERY_UI_THEME,
        'DEVILRY_STATIC_URL': settings.DEVILRY_STATIC_URL,
        'DEVILRY_MAIN_PAGE': settings.DEVILRY_MAIN_PAGE,
        'DEVILRY_LOGOUT_URL': settings.DEVILRY_LOGOUT_URL,
        'DEVILRY_SYSTEM_ADMIN_EMAIL': settings.DEVILRY_SYSTEM_ADMIN_EMAIL,
        'DEVILRY_DATETIME_FORMAT': "Y-m-d H:i",
        'STATUS_NO_DELIVERIES': AssignmentGroup.NO_DELIVERIES,
        'STATUS_NOT_CORRECTED': AssignmentGroup.NOT_CORRECTED,
        'STATUS_CORRECTED_NOT_PUBLISHED': AssignmentGroup.CORRECTED_NOT_PUBLISHED,
        'STATUS_CORRECTED_AND_PUBLISHED': AssignmentGroup.CORRECTED_AND_PUBLISHED,
        'session': request.session,
        'DEVILRY_THEME_URL': settings.DEVILRY_THEME_URL,
        'DEVILRY_EXTJS_URL': settings.DEVILRY_EXTJS_URL,
        'DEVILRY_JQUERY_URL': settings.DEVILRY_JQUERY_URL,
        'DEVILRY_MARKITUP_URL': settings.DEVILRY_MARKITUP_URL,
    }
