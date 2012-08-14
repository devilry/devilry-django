Ext.define('devilry_student.view.groupinfo.DeliveryPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_delivery',
    ui: 'lookslike-parawitheader-panel',
    margin: '20 20 20 20',

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
            cls: 'devilry_student_groupinfo_delivery devilry_student_groupinfo_delivery_' + (this._hasFeedback()? 'hasfeedback': 'nofeedback'),
            title: interpolate(gettext('%(delivery)s %(number)s'), {
                delivery: gettext('Delivery'),
                number: this.delivery.number
            }, true),

            items: [{
                xtype: 'box',
                tpl: this.bodyTpl,
                cls: 'bootstrap',
                data: {
                    latest_feedback: latest_feedback
                }
            }]
        });
        this.callParent(arguments);
    },

    _hasFeedback: function() {
        return this.delivery.feedbacks.length > 0;
    }
});
