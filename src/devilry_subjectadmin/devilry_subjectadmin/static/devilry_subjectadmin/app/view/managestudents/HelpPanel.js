Ext.define('devilry_subjectadmin.view.managestudents.HelpPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudents_help',
    cls: 'bootstrap',

    tpl: [
        '<h2>', gettext('Help'), '</h2>',

        '<h3>', gettext('Groups'), '</h3>',
        '<p>',
            '<strong class="text-warning">', gettext('IMPORTANT'), ': </strong>',
            gettext('{Students_term} are always in a group.'),
            ' <small class="muted">',
            gettext('Even when {students_term} make individual deliveries, they are organized into groups. Each student is added to their own group when you add them to an assignment. This means that the list to your left is all groups registered on this assignment.'),
            '</small>',
        '</p>',

        '<h4>', gettext('How to create project groups'), '</h4>',
        '<p>',
            gettext('Select two or more groups, and choose <em>Create project group</em>.'),
        '</p>',
        '<p>',
            '<span class="text-success">',
                gettext('TIP'),
            ':</span> ',
            gettext('Use <em>Select by search</em> to efficiently select students.'),
        '</p>',

        '<h3>', gettext('Examiners'), '</h3>',
        '<p>',
            '<strong class="text-warning">', gettext('IMPORTANT'), ': </strong>',
            gettext('You are administrator, which is NOT the same as examiner.'),
            ' <small class="muted">',
                gettext('If you want to provide feedback to some groups, you have to make yourself examiner on those groups.'),
            '</small>',
        '</p>',

        '<p>',
        '</p>',

        '<h4>', gettext('How to set {examiners_term}'), '</h4>',
        '<p>',
            gettext('To set {examiners_term} on a single group, select the group and use the edit button in the {examiner_term} heading on your right hand side.'),
        '</p>',
        '<p>',
            gettext('To set {examiners_term} on multiple groups, select the groups and use the buttons in the <em>Manage {examiners_term}</em> section.'),
        '</p>',


        '<h3>', gettext('Find/select efficiently'), '</h3>',
        '<p>',
            gettext('Selecting students from the list using the checkboxes works if you have few students. For huge {subjects_term}, manual selection is rarely useful.'),
        '</p>',
        '<h4>', gettext('Select by pre-defined filters'), '</h4>',
        '<p>',
            gettext('The <em>Select</em>-button in the lower left corner lets you select groups using a good set of pre-defined filters.'),
        '</p>',
        '<p>',
            gettext('The <em>Add to selection</em>-button contains the same filters. Instead of replacing the current selection, filters in that menu keeps the currently selected groups, and adds any matching groups to the selection.'),
        '</p>',
        '<h4 id="select-by-search-help">', gettext('Select by search'), '</h4>',
        '<p>',
            gettext('The search field at the bottom of the window allows you to search for groups. The results is displayed in a menu, and when you select a group from the menu, the group is selected.'),
        '</p>',

        '<h3>', gettext('On a small or huge display?'), '</h3>',
        '<p>',
            gettext('The scale of the group-list, and the selection-grid (when multiple groups are selected), is not perfect for all displays. To amend this, we allow you to resize these lists. Move your cursor over the inner border of one of these lists, and a resize-indicator will apear. Your selected sizes is saved as a cookie in your browser, which means that they will be remembered when you return to this view in your current browser.'),
        '</p>'
    ],

    data: {
        Students_term: gettext('Students'),
        students_term: gettext('students'),
        examiners_term: gettext('examiners'),
        subjects_term: gettext('subjects')
    }
});
