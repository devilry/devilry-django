Ext.define('devilry_subjectadmin.view.managestudents.MergeGroups', {
    extend: 'Ext.container.Container',
    alias: 'widget.mergegroups',
    cls: 'devilry_subjectadmin_mergegroups',
    requires: [
        'devilry_extjsextras.MoreInfoBox'
    ],


    merge_introtext: gettext('Multiple students on a single group is used when students cooperate on an assignment. Such project groups have the following properties:'),
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
        this.mergehelp = this._createMergeHelp();
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'box',
                anchor: '100%',
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
                xtype: 'moreinfobox',
                itemId: 'mergeGroupsHelp',
                anchor: '100%',
                introtext: this.merge_introtext,
                cls: 'merge_groups_helpbox',
                moreWidget: {
                    xtype: 'box',
                    html: this.mergehelp
                }
            }, {
                xtype: 'button',
                scale: 'medium',
                cls: 'merge_groups_button',
                text: gettext('Create project group'),
                itemId: 'mergeGroupsButton',
                margin: '0 0 20 0' // NOTE: This is because "More info" seems to cause the rendering of the padding on the container to sometimes not apply, and we want some space below the button
            }, {
                xtype: 'panel',
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
        });
        this.callParent(arguments);
    }
});
