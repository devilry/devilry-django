/** Re-usable help strings for basenode fields. */
Ext.define('devilry_subjectadmin.utils.BaseNodeHelp', {
    singleton: true,

    getShortNameHelp: function() {
        return gettext("A short name with at most 20 letters. Can only contain lowercase english letters (a-z), numbers, underscore ('_') and hyphen ('-'). This is used the the regular name takes to much space.");
    },

    getLongNameHelp: function() {
        return gettext("May contain any characters, including language-specific characters.");
    },

    getShortAndLongNameHelp: function() {
        return [
            gettext('Choose a long and a short name. Short name is used in places where long name takes too much space, such as table headers and navigation.'),
            gettext("The short name can contain up to 20 letters, and it can only contain lowercase english letters (<em>a-z</em>), <em>numbers</em>, <em>'_'</em> and <em>'-'</em>.")
        ].join(' ');
    }
});
