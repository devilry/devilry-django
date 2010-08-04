from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from devilry.core.models import Node, Subject, Period, Assignment


def simpleview(request, *args):
    return mark_safe(u"""Examiner dashboard-view(s) is not finished.
        <a href='/examiner/choose-assignment'>Click here</a> for the
        main examiner view.""")


def list_deliveries(request, *args):
    pass
