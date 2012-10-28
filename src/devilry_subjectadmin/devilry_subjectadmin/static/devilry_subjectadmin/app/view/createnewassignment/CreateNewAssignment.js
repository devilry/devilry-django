Ext.define('devilry_subjectadmin.view.createnewassignment.CreateNewAssignment' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewassignment',
    requires: [
        'devilry_extjsextras.PrimaryButton'
    ],

    /**
     * @cfg period_id
     */

    border: 0,
    bodyPadding: '20 40 20 40',
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'pageHeading',
                tpl: [
                    '<h1>',
                        '{heading}',
                        '<tpl if="subheading">',
                            ' <small> - {subheading}</small>',
                        '</tpl>',
                    '</h1>'
                ],
                data: {
                    heading: gettext('Create new assignment'),
                    subheading: undefined
                }
            }, {
                margin: '10 0 0 0',
                xtype: 'container',
                items: { // Note: We wrap this in an extra container to avoid that the create button ends up at the bottom of the screen
                    xtype: 'createnewassignmentform',
                    period_id: this.period_id
                }
            }]
        });
        this.callParent(arguments);
    }
});
