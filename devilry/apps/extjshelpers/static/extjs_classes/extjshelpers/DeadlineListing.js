/** Deadline listing.
 *
 * Lists DeadlineInfo's.
 *
 * @xtype deadlinelisting
 */
Ext.define('devilry.extjshelpers.DeadlineListing', {
    extend: 'Ext.container.Container',
    alias: 'widget.deadlinelisting',
    cls: 'widget-deadlinelisting',
    requires: [
        'devilry.extjshelpers.DeadlineInfo'
    ],

    config: {
        assignmentgroupid: undefined
    },

    initComponent: function() {
        this.callParent(arguments);
        this.loadDeadlines();
    },

    loadDeadlines: function() {
        var deadlinestoreid = 'devilry.apps.examiner.simplified.SimplifiedDeadlineStore';
        var deadlinestore = Ext.data.StoreManager.lookup(deadlinestoreid);
        deadlinestore.proxy.extraParams.orderby = Ext.JSON.encode(['-number']);
        deadlinestore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'assignment_group',
            comp: 'exact',
            value: this.assignmentgroupid
        }]);

        deadlinestore.load({
            scope: this,
            callback: this.onLoadDeadlines
        });
    },

    onLoadDeadlines:function(deadlinerecords) {
        var me = this;
        Ext.each(deadlinerecords, function(deadlinerecord) {
            me.addDeadline(deadlinerecord.data);
        });
    },

    addDeadline:function(deadline) {
        this.add({
            xtype: 'deadlineinfo',
            deadline: deadline
        });
    }
});
