Ext.define('devilry_subjectadmin.view.managestudents.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.admingroupinfo_deadline',
    cls: 'devilry_subjectadmin_admingroupinfo_deadline',
    collapsible: true,
    collapsed: true,
    titleCollapse: true,
    animCollapse: false,

    requires: [
        'devilry_extjsextras.DatetimeHelpers',
        'devilry_subjectadmin.view.managestudents.DeliveryPanel'
    ],

    /**
     * @cfg {Object} [deadline]
     */

    /**
     * @cfg {Object} [active_feedback]
     */

    headerTpl: [
        '<div class="bootstrap deadlineheader">',
            '<div class="lineone">',
                '<span class="linklike">',
                    '<em class="deadline_label">{deadline_term}</em>: ',
                    '<span class="deadline">{deadline_formatted}</span>',
                '</span>',
                '<span class="in_the_future">',
                    '<tpl if="in_the_future">',
                        '<span class="success"> ({offset_from_now})</span>',
                    '<tpl else>',
                        '<span class="danger"> ({offset_from_now})</span>',
                    '</tpl>',
                '</span>',
            '</div>',
            '<div class="linetwo">',
                '<small><em>{deliveries_term}</em>: <span class="deliverycount">{delivery_count}</span></small>',
                '<tpl if="text">',
                    '&nbsp;',
                    '&nbsp;',
                    '&nbsp;',
                    '<small><em>{text_title}</em>: {text}</small>',
                '</tpl>',
            '</div>',
        '</div>'
    ],

    deadlineTextTpl: [
        '<tpl if="deadline.text">',
            '<h2>',
                gettext('About this deadline'),
            '</h2>',
            '<p style="white-space: pre-wrap;">{deadline.text}</p>',
        '</tpl>'
    ],

    _formatDeadlineTextOneline: function() {
        var maxlength = 50;
        var text = this.deadline.text;
        if(text === null || text.length === 0) {
            return null;
        }
        text = text.replace(/(\r\n|\n|\r)/gm, " ");
        return Ext.String.ellipsis(text, maxlength);
    },

    initComponent: function() {
        var deadline_datetime = devilry_subjectadmin.model.AggregatedGroupInfo.parseDateTime(this.deadline.deadline);
        var deadline_formatted = Ext.Date.format(deadline_datetime, 'Y-m-d H:i:s');
        var offset_from_now = this.deadline.offset_from_now;
        offset_from_now = devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
            offset_from_now, this.deadline.in_the_future);

        Ext.apply(this, {
            itemId: Ext.String.format('deadline-{0}', this.deadline.id),
            id: Ext.String.format('deadlinepanel-{0}', this.deadline.id),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                delivery_count: this.deadline.deliveries.length,
                deliveries_term: gettext('Deliveries'),
                offset_from_now: offset_from_now,
                in_the_future: this.deadline.in_the_future,
                text_title: gettext('About this deadline'),
                text: this._formatDeadlineTextOneline()
            }),
            items: [{
                xtype: 'box',
                cls: 'bootstrap deadlinetext',
                tpl: this.deadlineTextTpl,
                hidden: Ext.isEmpty(this.deadline.text),
                padding: '20',
                data: {
                    deadline: this.deadline
                }
            }, {
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
        Ext.Array.each(this.deadline.deliveries, function(delivery, index_in_deadline) {
            configs.push({
                xtype: 'admingroupinfo_delivery',
                delivery: delivery,
                index_in_deadline: index_in_deadline,
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
