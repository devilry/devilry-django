Ext.define('devilry.student.AddDeliveriesContainer', {
    extend: 'Ext.container.Container',
    alias: 'widget.add_deliveries_container',
    cls: 'widget-add_deliveries_container',
    autoScroll: true,
    border: false,
    requires: [
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.student.FileUploadPanel',
        'devilry.student.DeadlineTitle'
    ],

    config: {
        assignmentgroupid: undefined,
        deadlineid: undefined,
        deliverymodelname: undefined,
        latest_deadline: undefined,
        ag_model: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var agroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.ag_model.load(this.assignmentgroupid, {
            success: function(record) {
                Ext.getBody().unmask();
                agroup_recordcontainer.setRecord(record);
            }
        });

        Ext.apply(this, {
            items: [{
                xtype: 'deadlinetitle',
                singlerecordontainer: agroup_recordcontainer,
                flex: 1,
                extradata: {
                    latest_deadline: this.latest_deadline
                }
            }, {
                flex: 1,
                margin: { top: 20 },
                xtype: 'fileuploadpanel',
                bodyPadding: 20,
                assignmentgroupid: this.assignmentgroupid,
                deadlineid: this.deadlineid,
                initialhelptext: 'Upload files for your delivery. You can upload multiple files.',
                deliverymodelname: this.deliverymodelname,
                agroup_recordcontainer: agroup_recordcontainer
            }]
        });
        this.callParent(arguments);
    }

    
});
