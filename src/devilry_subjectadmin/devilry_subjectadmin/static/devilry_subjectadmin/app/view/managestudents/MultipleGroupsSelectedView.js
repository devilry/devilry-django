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
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.form.Help',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ManageTagsOnMultiple'
    ],

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */



    //
    //
    // Tag help
    //
    //

    tag_introtext: interpolate(gettext('%(Tags_term)s is a flexible method of organizing %(groups_term)s. Only administrators can see %(tags_term)s. You can search and select %(groups_term)s by their %(tags_term)s. Common use-cases are:'), {
        Tags_term: gettext('Tags'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags')
    }, true),

    tag_details_points: [
        interpolate(gettext('Mark %(groups_term)s with special needs.'), {
            groups_term: gettext('groups')
        }, true),
        interpolate(gettext('Organize %(groups_term)s attending the same classroom sessions.'), {
            groups_term: gettext('groups')
        }, true),
        gettext('Mark suspected cheaters.')
    ],

    tag_details_periodnote: interpolate(gettext('<strong>NOTE:</strong> %(Tags_term)s on %(groups_term)s must not be confused with %(tags_term)s on %(students_term)s and %(examiners_term)s on a %(period_term)s. Those %(tags_term)s are used to automate assigning examiners to students. %(Tags_term)s from the %(period_term)s may have been included when you added %(groups_term)s to this %(assignment_term)s, however you can safely edit %(tags_term)s on %(groups_term)s without affecting the %(tags_term)s on the %(period_term)s.'), {
        Tags_term: gettext('Tags'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags'),
        examiners_term: gettext('examiners'),
        students_term: gettext('students'),
        period_term: gettext('period'),
        assignment_term: gettext('assignment')
    }, true),

    _createTagMoreHelp: function() {
        return Ext.create('Ext.XTemplate', 
            '<ul>',
                '<tpl for="points">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>',
            '<p>',
                this.tag_details_periodnote,
            '</p>'
        ).apply({
            points: this.tag_details_points
        });
    },


    //
    //
    // Merge help
    //
    //

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

                // Tags
                }, {
                    xtype: 'managetagsonmultiple',
                    margin: buttonmargin
                
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
                    xtype: 'moreinfobox',
                    itemId: 'mergeGroupsHelp',
                    margin: helpmargin,
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
