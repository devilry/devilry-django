Ext.define('devilry_subjectadmin.view.managestudents.HelpPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudents_help',
    cls: 'bootstrap',

    tpl: [
        '<h3>', gettext('How to set {examiners_term}'), '</h3>',
        '<p>',
            gettext('To set {examiners_term} on a single {group_term}, select the {group_term} and use the edit button in the {examiner_term} heading on your right hand side.'),
        '</p>',
        '<p>',
            gettext('To set {examiners_term} on multiple {groups_term}, select the {groups_term} and use the buttons in the <em>Manage {examiners_term}</em> section.'),
        '</p>',

        '<h3>', gettext('How to create project groups'), '</h3>',
        '<p>',
            gettext('Select two or more groups, and choose <em>Create project group</em>.'),
        '</p>'
    ],

    data: {
        examiners_term: gettext('examiners'),
        groups_term: gettext('groups'),
        group_term: gettext('group')
    }
});
