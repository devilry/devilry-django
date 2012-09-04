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
        'devilry_extjsextras.PrimaryButton'
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
                        heading: gettext('Set tag(s)'),
                    }
                }, {
                    xtype: 'container',
                    items: [{
                        xtype: 'panel',
                        border: false,
                        frame: false,
                        layout: 'fit',
                        dockedItems: [{
                            xtype: 'toolbar',
                            dock: 'top',
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
                                tooltip: gettext('Replace the tags on the selected groups with one or more new tag(s).')
                            }, {
                                text: gettext('Add tag(s)'),
                                itemId: 'addTagsButton',
                                tooltip: gettext('Add one or more tag(s) to the selected groups.')
                            }, {
                                text: gettext('Clear tags'),
                                itemId: 'clearTagsButton',
                                icon: devilry_theme.Icons.DELETE_SMALL,
                                tooltip: gettext('Remove/clear all tags from the selected groups.')
                            }]
                        }],
                        items: {
                            xtype: 'box',
                            margin: '10 0 0 0',
                            cls: 'bootstrap',
                            html: [
                                '<p class="muted">',
                                    gettext('Assign one or more tag(s) to the selected groups. Use the arrow button for methods of setting tags, such as random and by tags. Setting tags <strong>replaces</strong> the current tags.'),
                                '</p>'
                            ]
                        }
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
