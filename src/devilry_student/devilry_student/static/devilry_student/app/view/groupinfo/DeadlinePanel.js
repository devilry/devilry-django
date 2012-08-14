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

    headerTpl: [
        '<div class="linklike">',
            '<em class="deadline_text">{deadline_text}</em>: ',
            '<span class="deadline_datetime">{deadline_datetime}</span>',
        '</div>',
        '<div class="metadata"><small>meta</small></div>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_text: gettext('Deadline'),
                deadline_datetime: this.deadline.deadline
            }),
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
