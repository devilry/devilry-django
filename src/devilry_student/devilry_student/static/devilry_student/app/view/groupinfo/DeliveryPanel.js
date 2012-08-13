Ext.define('devilry_student.view.groupinfo.DeliveryPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_delivery',
    cls: 'devilry_student_groupinfo_delivery',

    /**
     * @cfg {Object} [delivery]
     */

    bodyTpl: [
        '<tpl if="latest_feedback">',
            '{latest_feedback.rendered_view}',
        '<tpl else>',
            gettext('No feedback'),
        '</tpl>'
        
    ],

    initComponent: function() {
        var latest_feedback = this.delivery.feedbacks[0];
        Ext.apply(this, {
            title: interpolate(gettext('%(delivery)s %(number)s'), {
                delivery: gettext('Delivery'),
                number: this.delivery.number
            }, true),
            items: [{
                xtype: 'box',
                tpl: this.bodyTpl,
                data: {
                    latest_feedback: latest_feedback
                }
            }]
        });
        this.callParent(arguments);
    }
});
