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
        'devilry_subjectadmin.view.managestudents.ManageExaminersOnMultiple',
        'devilry_subjectadmin.view.managestudents.ManageTagsOnMultiple',
        'devilry_subjectadmin.view.managestudents.MergeGroups'
    ],

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */


    initComponent: function() {
        var buttonmargin = '30 0 0 0';
        var helpmargin = '4 0 0 0';

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
                    xtype: 'manageexaminersonmultiple'
                    //xtype: 'splitbutton',
                    //margin: 0,
                    //scale: 'medium',
                    //text: gettext('Set examiner(s)'),
                    //itemId: 'setExaminersButton',
                    //menu: [{
                        //text: gettext('Add examiner(s)'),
                        //itemId: 'addExaminersButton',
                        //tooltip: gettext('Add one or more examiner(s) to the selected groups.')
                    //}, {
                        //text: gettext('Clear examiners'),
                        //itemId: 'clearExaminersButton',
                        //icon: devilry_theme.Icons.DELETE_SMALL,
                        //tooltip: gettext('Remove/clear all examiners from the selected groups.')
                    //}]
                //}, {
                    //xtype: 'formhelp',
                    //margin: helpmargin,
                    //anchor: '100%',
                    //html: gettext('Assign one or more examiner(s) to the selected groups. Use the arrow button for methods of setting examiners. Setting examiners <strong>replaces</strong> the current examiners.')



                }, {
                    xtype: 'managetagsonmultiple',
                    margin: buttonmargin
                }, {
                    xtype: 'mergegroups',
                    margin: buttonmargin
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
