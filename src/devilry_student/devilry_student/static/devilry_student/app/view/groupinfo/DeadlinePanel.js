Ext.define('devilry_student.view.groupinfo.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_deadline',
    cls: 'devilry_student_groupinfo_deadline',
    collapsible: true,
    collapsed: true,
    titleCollapse: true,
    animCollapse: false,

    /**
     * @cfg {Object} [deadline]
     */

    /**
     * @cfg {Object} [active_feedback]
     */

    headerTpl: [
        '<div class="linklike">',
            '<em class="deadline_label">{deadline_term}</em>: ',
            '<span class="deadline">{deadline_formatted}</span>',
        '</div>',
        '<div class="metadata"><small><em>{deliveries_term}</em>: {delivery_count}</small></div>'
    ],

    initComponent: function() {
        var deadline_datetime = devilry_student.model.GroupInfo.parseDateTime(this.deadline.deadline);
        var deadline_formatted = Ext.Date.format(deadline_datetime, 'Y-m-d h:i:s');
        Ext.apply(this, {
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                delivery_count: this.deadline.deliveries.length,
                deliveries_term: gettext('Deliveries')
            }),
            items: []
        });
        Ext.Array.each(this.deadline.deliveries, function(delivery) {
            this.items.push({
                xtype: 'groupinfo_delivery',
                delivery: delivery,
                active_feedback: this.active_feedback
            });
        }, this);
        this.callParent(arguments);
    }
});
