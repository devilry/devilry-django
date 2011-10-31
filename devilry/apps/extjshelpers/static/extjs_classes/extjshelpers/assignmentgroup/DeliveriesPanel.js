Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriespanel',
    requires: [
        'devilry.extjshelpers.assignmentgroup.IsOpen',
    ],

    config: {
        assignmentgroup_recordcontainer: undefined,
        delivery_recordcontainer: undefined,
        deadlineRecord: undefined,
        deliveriesStore: undefined,
        activeFeedback: undefined
    },

    titleTpl: Ext.create('Ext.XTemplate',
        '<div class="deadline_title">',
        '    <div style="font-weight:bold">Deadline: ',
        '        <tpl if="assignmentgroup.parentnode__delivery_types !== 1">{deadline.deadline:date}</tpl>',
        '        <tpl if="assignmentgroup.parentnode__delivery_types === 1">Not defined in Devilry</tpl>',
        '    </div>',
        '    <div>',
        //'        Deliveries: <span class="number_of_deliveries">{deadline.number_of_deliveries}</span>',
        '        <tpl if="deadline.number_of_deliveries &gt; 0">{extra}</tpl>',
        '    </div>',
        '<div>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var extra = '(No feedback)';
        if(this.activeFeedback) {
            extra = Ext.String.format('(Latest feedback: {0})', this.activeFeedback.data.grade);
        }

        Ext.apply(this, {
            title: this.titleTpl.apply({
                deadline: this.deadlineRecord.data,
                assignmentgroup: this.assignmentgroup_recordcontainer.record.data,
                extra: extra
            }),
            layout: 'fit',
            border: false,
            listeners: {
                scope: this,
                collapse: this._onCollapse
            }
            //tbar: [{
                //xtype: 'button',
                //iconCls: 'icon-edit-16',
                //text: 'Edit deadline',
                //listeners: {
                    //scope: this,
                    //click: this.onEditDeadline
                //}
            //}, {
                //xtype: 'button',
                //iconCls: 'icon-delete-16',
                //text: 'Delete deadline',
                //listeners: {
                    //scope: this,
                    //click: this.onDeleteDeadline
                //}
            //}]
        });

        if(this.deliveriesStore.count() === 0) {
            this.items = {
                xtype: 'box',
                html: 'No deliveries on this deadline.',
                padding: 10
            };
        } else {
            this.items = {
                xtype: 'deliveriesgrid',
                delivery_recordcontainer: this.delivery_recordcontainer,
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                store: this.deliveriesStore
            };
        }

        this.callParent(arguments);
    },

    _onCollapse: function() {
        //var allGrids = this.up('assignmentgroupoverview').feedbackPanel.hide();
    },

    /**
     * @private
     */
    onEditDeadline: function() {
        console.log('Edit deadline');
    },

    onDeleteDeadline: function() {
        console.log('Delete deadline');
    }
});
