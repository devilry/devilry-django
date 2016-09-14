from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType


class PointsPlugin(PluginType):

    plugintypeid = 'devilry_qualifiesforexam.plugin_points'
    human_readable_name = 'Students must get a minimum number of points'
    description = 'Choose this option if you require your students to to get a minimum number of points in total ' \
                  'on all or some of the assignments to qualify for final exam. ' \
                  'All assignments are selected by default.'
