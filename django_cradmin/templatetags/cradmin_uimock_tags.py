import logging

from django import template
from django.urls import reverse

register = template.Library()
log = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def cradmin_uimock_url(context, mockname=None, viewname=None):
    """
    Reverse the URL of a :class:`django_cradmin.viewhelpers.uimock.UiMock` view.

    Args:
        mockname (str): Name of the mock to link to (the name of the template without ``.django.html``).
            If this is not specified, we link to ``index.django.html``.
        viewname: The name of the mock view (the name specified for the view in urls.py).
            You do not need to specify this to link to mocks within the same view.
    """
    request = context["request"]
    if viewname:
        path = reverse(viewname)
    else:
        path = request.path
        if not path.endswith("/"):
            path = path.rsplit("/", 1)[0] + "/"
    if mockname:
        path = "{}{}".format(path, mockname)
    return path
