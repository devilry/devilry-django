Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesPanel', {
    extend: 'Ext.container.Container',
    alias: 'widget.deliveriespanel',
    requires: [
        'devilry.extjshelpers.assignmentgroup.IsOpen',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    assignmentgroup_recordcontainer: undefined,
    delivery_recordcontainer: undefined,
    deadlineRecord: undefined,
    deliveriesStore: undefined,
    activeFeedback: undefined,

    titleTpl: [
        '<div class="deadline_title bootstrap">',
            '<p style="padding: 5px; margin: 0;">',
                '<tpl if="assignmentgroup.parentnode__delivery_types !== 1">',
                    '<small class="muted" style="line-height: 14px;">', gettext('Deadline'), ':</small> ',
                    '<strong style="font-size: 16px;">{[this.formatDatetime(values.deadline.deadline)]}</strong>',
                '</tpl>',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    gettext('Non-electronic delivery'),
                '</tpl>',
            '</p>',
        '</div>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            }
        }
    ],


    initComponent: function() {
        Ext.apply(this, {
            border: false,
            margin: '0 0 20 0'
        });

        this.items = [{
            xtype: 'box',
            tpl: this.titleTpl,
            data: {
                deadline: this.deadlineRecord.data,
                assignmentgroup: this.assignmentgroup_recordcontainer.record.data
            }
        }];
        if(this.deliveriesStore.count() === 0) {
            this.items.push({
                xtype: 'box',
                cls: 'bootstrap',
                html: [
                    '<p class="muted" style="margin: 0 0 0 5px; padding: 0;">',
                        gettext('No deliveries on this deadline'),
                    '</p>'
                ]
            });
        } else {
            this.items.push({
                xtype: 'deliveriesgrid',
//                margin: '0 0 0 20',
                delivery_recordcontainer: this.delivery_recordcontainer,
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                deadlineRecord: this.deadlineRecord,
                store: this.deliveriesStore
            });
        }

        this.callParent(arguments);
    },

    _onCollapse: function() {
        //var allGrids = this.up('assignmentgroupoverview').feedbackPanel.hide();
    }
});
