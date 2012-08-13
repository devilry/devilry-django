Ext.define('devilry_student.view.groupinfo.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_deadline',
    cls: 'devilry_student_groupinfo_deadline',

    /**
     * @cfg {Object} [deadline]
     */

    initComponent: function() {
        Ext.apply(this, {
            title: interpolate(gettext('%(deadline)s: %(deadline_datetime)s'), {
                deadline: gettext('Deadline'),
                deadline_datetime: this.deadline.deadline
            }, true),
            items: []
        });
        Ext.Array.each(this.deadline.deliveries, function(delivery) {
            this.items.push({
                xtype: 'groupinfo_delivery',
                delivery: delivery
            });
        }, this);
        this.callParent(arguments);
    }
});
