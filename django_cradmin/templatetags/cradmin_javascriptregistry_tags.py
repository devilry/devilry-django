from django.template import Library
from django_cradmin import javascriptregistry
from django_cradmin.javascriptregistry.default_componentids import get_default_component_ids
from django_cradmin.utils import cradmin_collections

register = Library()


class JavascriptRegistryTemplateTagError(Exception):
    pass


def _get_components_from_context(context):
    if "request" not in context:
        raise JavascriptRegistryTemplateTagError(
            "The request variable is not in the template context. "
            'You can get this using the "django.template.context_processors.request" context processor.'
        )
    if "cradmin_javascriptregistry_component_ids" in context:
        component_ids = context["cradmin_javascriptregistry_component_ids"]
    else:
        component_ids = get_default_component_ids()

    request = context["request"]
    registry = javascriptregistry.Registry.get_instance()
    components = registry.get_component_objects(request=request, component_ids=component_ids)
    return components


def _get_sourceurls_from_components(components, methodname):
    all_sourceurls = cradmin_collections.OrderedSet()
    for component in components:
        sourceurls = getattr(component, methodname)()
        for sourceurl in sourceurls:
            all_sourceurls.add(sourceurl)
    return all_sourceurls


def _get_javascript_code_from_components(components, methodname):
    javascript_code_list = []
    for component in components:
        javascript_code = getattr(component, methodname)()
        if javascript_code:
            javascript_code = javascript_code.strip()
            if javascript_code:
                javascript_code_list.append(javascript_code)
    all_javascript_code = "\n".join(javascript_code_list)
    return all_javascript_code


@register.inclusion_tag(
    "django_cradmin/templatetags/javascriptregistry/script_tags_from_sourceurls.django.html", takes_context=True
)
def cradmin_javascriptregistry_head(context):
    """
    Renders the jsregistry code for the ``<head>`` tag.

    Raises:

    """
    return {
        "sourceurls": _get_sourceurls_from_components(
            components=_get_components_from_context(context=context), methodname="get_head_sourceurls"
        )
    }


@register.inclusion_tag("django_cradmin/templatetags/javascriptregistry/end_of_body.django.html", takes_context=True)
def cradmin_javascriptregistry_end_of_body(context):
    """
    Renders the jsregistry code for the end of the ``<body>`` tag.
    """
    components = _get_components_from_context(context=context)
    return {
        "sourceurls": _get_sourceurls_from_components(components=components, methodname="get_sourceurls"),
        "javascript_code_before_sourceurls": _get_javascript_code_from_components(
            components=components, methodname="get_javascript_code_before_sourceurls"
        ),
        "javascript_code_after_sourceurls": _get_javascript_code_from_components(
            components=components, methodname="get_javascript_code_after_sourceurls"
        ),
    }
