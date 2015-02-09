from django.utils.translation import ugettext_lazy as _


def make_settings_summary_points(status):
    settings = status.devilry_qualifiesforexam_points_pointspluginsetting
    longnames = [selected.assignment.long_name for selected in settings.pointspluginselectedassignment_set.all()]
    longnames = ', '.join(longnames)
    return u'{minimumlabel}: {minimum_points}. {selectedlabel}: {selected}.'.format(
            minimumlabel = _(u'Minimum points'),
            minimum_points = settings.minimum_points,
            selectedlabel = _(u'Selected assignments'),
            selected = longnames
            )
