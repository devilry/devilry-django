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
        var deadline_formatted = Ext.Date.format(deadline_datetime, 'Y-m-d H:i:s');

        Ext.apply(this, {
            itemId: Ext.String.format('deadline-{0}', this.deadline.id),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                delivery_count: this.deadline.deliveries.length,
                deliveries_term: gettext('Deliveries')
            }),
            items: [{
                xtype: 'container',
                itemId: 'addDeliveryPanelContainer'
            }, {
                xtype: 'container',
                itemId: 'deliveriesContainer',
                items: this._getDeliveryPanelConfigs()
            }]
        });
        this.callParent(arguments);
    },

    _getDeliveryPanelConfigs: function() {
        var configs = [];
        Ext.Array.each(this.deadline.deliveries, function(delivery) {
            configs.push({
                xtype: 'groupinfo_delivery',
                delivery: delivery,
                active_feedback: this.active_feedback
            });
        }, this);
        return configs;
    },

    hideDeliveries: function() {
        this.down('#deliveriesContainer').hide();
    },

    showDeliveries: function() {
        this.down('#deliveriesContainer').show();
    }
});
