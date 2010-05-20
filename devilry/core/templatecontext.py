from django.conf import settings


def template_variables(request):
    return {
        'JQUERY_UI_THEME': settings.JQUERY_UI_THEME,
        'DEVILRY_RESOURCES_URL': settings.DEVILRY_RESOURCES_URL,
        'BASE_TEMPLATE': settings.BASE_TEMPLATE,
        'DEVILRY_DATETIME_FORMAT': "Y-m-d G:i",
    }
