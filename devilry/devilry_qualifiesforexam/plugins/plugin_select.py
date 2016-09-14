from devilry.devilry_qualifiesforexam.plugintyperegistry import PluginType


class SelectPlugin(PluginType):

    plugintypeid = 'devilry_qualifiesforexam.plugin_select'
    human_readable_name = 'Select assignments'
    description = 'Choose this option if you require your students to get a passing grade on the assignments ' \
                  'you select. All assignments are selected by default.'
