Ext.define('devilry.student.AddDeliveriesContainer', {
    extend: 'Ext.container.Container',
    alias: 'widget.add_deliveries_container',
    cls: 'widget-add_deliveries_container',
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
        deadline_modelname: undefined,
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

        this.center = Ext.widget('container', {
            margin: { top: 20 },
            flex: 1,
            layout: {
                type: 'hbox',
                align: 'stretchmax'
            },
            style: 'background-color: transparent',
            autoScroll: true,
            items: [{
                flex: 7,
                xtype: 'fileuploadpanel',
                bodyPadding: 20,
                assignmentgroupid: this.assignmentgroupid,
                deadlineid: this.deadlineid,
                initialhelptext: 'Upload files for your delivery. You can upload multiple files.',
                deliverymodelname: this.deliverymodelname,
                agroup_recordcontainer: agroup_recordcontainer
            }]
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'deadlinetitle',
                singlerecordontainer: agroup_recordcontainer,
                extradata: {
                    latest_deadline: this.latest_deadline
                }
            }, this.center]
        });

        this.showDeadlineTextIfAny();
        this.callParent(arguments);
    },

    showDeadlineTextIfAny: function() {
        Ext.ModelManager.getModel(this.deadline_modelname).load(this.deadlineid, {
            scope: this,
            success: function(record) {
                if(record.data.text) {
                    this.center.add({
                        xtype: 'panel',
                        title: 'About this deadline',
                        html: record.data.text,
                        style: 'white-space: pre-line',
                        width: 100,
                        margin: {left: 10},
                        bodyPadding: 10,
                        flex: 3
                    });
                }
            }
        });
    }
});
