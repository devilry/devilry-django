/**
 * A panel that displays information about multple groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'devilry_subjectadmin_multiplegroupsview',
    ui: 'transparentpanel',
    requires: [
        'devilry_theme.Icons',
        'devilry_extjsextras.form.Help',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.OkCancelPanel',
    ],

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */


    merge_groups_explained: [
        gettext('Any student in the group will be able to make deliveries on behalf of the group.'),
        gettext('Feedback will be given to the group as a whole, not to individual students in the group.'),
        gettext('If any of the selected groups already have any deadlines, deliveries or feedback, they will be moved into the new group.'),
        gettext('You can split up a group later, however any deliveries and feedback will follow all students on the group, even if they where made before you merged the groups into a single group in the first place.'),
        gettext('The name of the group and open/closed status will be copied from the first group you selected.')
    ],


    _createMergeHelp: function() {
        return Ext.create('Ext.XTemplate', 
            '<ul>',
                '<tpl for="notes">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>'
        ).apply({
            notes: this.merge_groups_explained
        });
    },

    initComponent: function() {
        var buttonmargin = '30 0 0 0';
        var helpmargin = '4 0 0 0';
        this.mergehelp = this._createMergeHelp();

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                //region: 'center',
                minHeight: 100,
                flex: 6,
                xtype: 'container',
                padding: 20,
                layout: 'anchor',
                itemId: 'scrollableBodyContainer',
                autoScroll: true,
                items: [{
                    xtype: 'alertmessage',
                    cls: 'top_infobox',
                    type: 'info',
                    message: [this.topMessage, this.multiselectHowto].join(' ')
                
                // Set examiners
                }, {
                    xtype: 'splitbutton',
                    margin: 0,
                    scale: 'medium',
                    text: gettext('Set examiner(s)'),
                    itemId: 'setExaminersButton',
                    menu: [{
                        text: gettext('Add examiner(s)'),
                        itemId: 'addExaminersButton',
                        tooltip: gettext('Add one or more examiner(s) to the selected groups.')
                    }, {
                        text: gettext('Clear examiners'),
                        itemId: 'clearExaminersButton',
                        icon: devilry_theme.Icons.DELETE_SMALL,
                        tooltip: gettext('Remove/clear all examiners from the selected groups.')
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    anchor: '100%',
                    html: gettext('Assign one or more examiner(s) to the selected groups. Use the arrow button for methods of setting examiners. Setting examiners <strong>replaces</strong> the current examiners.')

                // Set Tags
                }, {
                    xtype: 'box',
                    cls: 'bootstrap',
                    margin: buttonmargin,
                    tpl: [
                        '<h2>',
                            '{heading}',
                        '</h2>'
                    ],
                    data: {
                        heading: gettext('Manage tag(s)'),
                    }
                }, {
                    xtype: 'container',
                    itemId: 'manageTagsPanel',
                    layout: 'card',
                    items: [{
                        xtype: 'panel',
                        itemId: 'tagsHelpAndButtonsContainer',
                        id: 'multi_tags_help_and_buttons_container',
                        border: false,
                        frame: false,
                        layout: 'fit',
                        dockedItems: [{
                            xtype: 'toolbar',
                            dock: 'bottom',
                            ui: 'footer',
                            padding: 0,
                            defaults: {
                                xtype: 'button',
                                scale: 'medium',
                                minWidth: 100
                            },
                            items: [{
                                text: gettext('Set tag(s)'),
                                itemId: 'setTagsButton',
                                id: 'multi_set_tags_button',
                                tooltip: gettext('Replace the tags on the selected groups with one or more new tag(s).')
                            }, {
                                text: gettext('Add tag(s)'),
                                itemId: 'addTagsButton',
                                id: 'multi_add_tags_button',
                                tooltip: gettext('Add one or more tag(s) to the selected groups.')
                            }, {
                                text: gettext('Clear tags'),
                                itemId: 'clearTagsButton',
                                ui: 'danger',
                                id: 'multi_clear_tags_button',
                                tooltip: gettext('Remove/clear all tags from the selected groups.')
                            }]
                        }],
                        items: {
                            xtype: 'box',
                            margin: '10 0 0 0',
                            cls: 'bootstrap',
                            tpl: [
                                '<div class="muted">',
                                    '<p>',
                                        gettext('{Tags_term} is a flexible method of organizing {groups_term}. Only administrators can see {tags_term}. You can search and select {groups_term} by their {tags_term}. Common use-cases are:'),
                                    '</p>',
                                    '<ul>',
                                        '<li>',
                                            gettext('Mark groups with special needs.'),
                                        '</li>',
                                        '<li>',
                                            gettext('Organize {groups_term} attending the same classroom sessions.'),
                                        '</li>',
                                        '<li>',
                                            gettext('Mark suspected cheaters.'),
                                        '</li>',
                                    '</ul>',
                                    '<p>',
                                        gettext('NOTE: {Tags_term} on {groups_term} must not be confused with {tags_term} on {students_term} and {examiners_term} on a {period_term}. Those {tags_term} are used to automate assigning examiners to students. {Tags_term} from the {period_term} may have been included when you added {groups_term} to this {assignment_term}, however you can safely edit {tags_term} on {groups_term} without affecting the {tags_term} on the {period_term}.'),
                                    '</p>',
                                '</div>'
                            ],
                            data: {
                                Tags_term: gettext('Tags'),
                                groups_term: gettext('groups'),
                                tags_term: gettext('tags'),
                                examiners_term: gettext('examiners'),
                                students_term: gettext('students'),
                                period_term: gettext('period'),
                                assignment_term: gettext('assignment')
                            }
                        }
                    }, {
                        xtype: 'choosetagspanel',
                        itemId: 'setTagsPanel',
                        id: 'multi_set_tags_panel',
                        buttonText: gettext('Set tags')
                    }, {
                        xtype: 'choosetagspanel',
                        itemId: 'addTagsPanel',
                        id: 'multi_add_tags_panel',
                        buttonText: gettext('Add tags')
                    }, {
                        xtype: 'okcancelpanel',
                        itemId: 'clearTagsPanel',
                        id: 'multi_clear_tags_panel',
                        oktext: gettext('Clear tags'),
                        okbutton_ui: 'danger',
                        bodyPadding: 10,
                        html: [
                            '<p>',
                                gettext('Do you really want to clear all tags on the selected groups?'),
                            '</p>'
                        ].join('')
                    }]
                
                // Merge groups
                }, {
                    xtype: 'box',
                    cls: 'bootstrap',
                    margin: buttonmargin,
                    tpl: [
                        '<h2>',
                            '{heading}',
                            ' <small>- {subheading}</small>',
                        '</h2>'
                    ],
                    data: {
                        heading: gettext('Create project group'),
                        subheading: gettext('Merge selected into one group')
                    }
                }, {
                    xtype: 'box',
                    itemId: 'mergeGroupsHelp',
                    margin: helpmargin,
                    anchor: '100%',
                    cls: 'merge_groups_helpbox bootstrap',
                    html: ['<div class="muted">', this.mergehelp, '</div>'].join('')
                }, {
                    xtype: 'button',
                    scale: 'medium',
                    cls: 'merge_groups_button',
                    text: gettext('Create project group'),
                    itemId: 'mergeGroupsButton'
                }, {
                    xtype: 'panel',
                    margin: helpmargin,
                    anchor: '100%',
                    cls: 'bootstrap merge_groups_confirmcontainer',
                    itemId: 'confirmMergeGroupsContainer',
                    layout: 'fit',
                    hidden: true,
                    bodyPadding: 10,
                    items: {
                        xtype: 'box',
                        cls: 'bootstrap',
                        tpl: [
                            gettext('Merge selected groups into a single group?'),
                            '{mergehelp}'
                        ],
                        data: {
                            mergehelp: this.mergehelp
                        }
                    },
                    fbar: [{
                        xtype: 'button',
                        itemId: 'mergeGroupsCancelButton',
                        cls: 'merge_groups_cancel_button',
                        text: gettext('Cancel'),
                        margin: '0 10 0 0'
                    }, {
                        xtype: 'primarybutton',
                        itemId: 'mergeGroupsConfirmButton',
                        cls: 'merge_groups_confirm_button',
                        minWidth: 200,
                        text: gettext('Create project group')
                    }]
                }]
            }, {
                flex: 4,
                minHeight: 150,
                xtype: 'selectedgroupssummarygrid'
            }]
        });
        this.callParent(arguments);
    }
});
