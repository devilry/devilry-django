/** Re-usable help strings for basenode fields. */
Ext.define('devilry_subjectadmin.utils.BaseNodeHelp', {
    singleton: true,

    getShortNameHelp: function() {
        return gettext("A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ('_') and hyphen ('-'). This is used the the regular name takes to much space.");
    },

    getLongNameHelp: function() {
        return gettext("May contain any characters, including language-specific characters.");
    }
});
