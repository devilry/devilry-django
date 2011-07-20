/** AssignmentGroup info.
 *
 * @xtype assignmentgroupinfo
 */
Ext.define('devilry.extjshelpers.AssignmentGroupInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupinfo',
    cls: 'widget-assignmentgroupinfo',

    config: {
        store: undefined
    },

    //constructor: function(config) {
        //return this.callParent([config]);
    //},
    
    initComponent: function() {
        this.callParent(arguments);
    },
});
