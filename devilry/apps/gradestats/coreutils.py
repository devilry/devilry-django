from django.utils.translation import ugettext as _
from django.utils.formats import date_format

from ..core.models import Assignment


class AssignmentUtils(object):
    """ Collection of utilities extending the functionality of
    :class:`devilry.core.models.Assignment`. """

    @classmethod
    def tooltip_html(cls, assignment):
        info = dict(long_name=assignment.long_name)
        for field in ("short_name", "publishing_time", "pointscale",
                "must_pass", "anonymous"):
            info[field+"_label"] = Assignment._meta.get_field(field).verbose_name
            v = getattr(assignment, field)
            if isinstance(v, bool):
                if v: v = _("Yes")
                else: v = _("No")
            info[field] = v
        info["publishing_time"] = date_format(assignment.publishing_time,
                "DATETIME_FORMAT")
        title = """
        <div>
            <strong>%(long_name)s</strong>
            <dl>
                <dt>%(short_name_label)s</dt>
                <dd>%(short_name)s</dd>
                <dt>%(publishing_time_label)s</dt>
                <dd>%(publishing_time)s</dd>
                <dt>%(pointscale_label)s</dt>
                <dd>%(pointscale)s</dd>
                <dt>%(must_pass_label)s</dt>
                <dd>%(must_pass)s</dd>
                <dt>%(anonymous_label)s</dt>
                <dd>%(anonymous)s</dd>
            </dl>
        </div>""" % info
        return title
