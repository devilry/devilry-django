from django.conf import settings


def template_variables(request):
    return {
        'DEVILRY_RESOURCES_URL': settings.DEVILRY_RESOURCES_URL,
        'BASE_TEMPLATE': settings.BASE_TEMPLATE,
    }
