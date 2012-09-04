/**
 * A panel that displays information about multple groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'devilry_subjectadmin_multiplegroupsview',
    ui: 'transparentpanel',
    requires: [
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
                }, {
                    xtype: 'manageexaminersonmultiple'
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
