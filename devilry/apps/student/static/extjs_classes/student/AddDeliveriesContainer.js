Ext.define('devilry.student.AddDeliveriesContainer', {
    extend: 'Ext.container.Container',
    alias: 'widget.add_deliveries_container',
    cls: 'widget-add_deliveries_container',
    border: false,
    requires: [
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.student.FileUploadPanel',
        'devilry.student.DeadlineTitle',
        'devilry.student.stores.UploadedFileStore'
    ],

    config: {
        assignmentgroupid: undefined,
        deadlineid: undefined,
        deliverymodelname: undefined,
        latest_deadline: undefined,
        deadline_modelname: undefined,
        ag_modelname: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var agroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        Ext.ModelManager.getModel(this.ag_modelname).load(this.assignmentgroupid, {
            success: function(record) {
                Ext.getBody().unmask();
                agroup_recordcontainer.setRecord(record);
            }
        });

        this.uploadedFilesStore = Ext.create('devilry.student.stores.UploadedFileStore', {
            listeners: {
                scope: this,
                add: this.onAddToUploadFilesStore
            }
        });

        this.sidebar = Ext.widget('panel', {
            layout: 'accordion',
            flex: 3,
            margin: {left: 10},
            hidden: true,
            listeners: {
                scope: this,
                add: function(sidebar, component) {
                    sidebar.show();
                    //component.show();
                }
            }
        });
        this.center = Ext.widget('container', {
            flex: 1,
            layout: {
                type: 'hbox',
                align: 'stretchmax'
            },
            margin: {bottom: 10},
            style: 'background-color: transparent',
            autoScroll: true,
            items: [{
                flex: 7,
                xtype: 'fileuploadpanel',
                height: 280,
                bodyPadding: 20,
                assignmentgroupid: this.assignmentgroupid,
                deadlineid: this.deadlineid,
                initialhelptext: 'Upload files for your delivery. You can upload multiple files.',
                deliverymodelname: this.deliverymodelname,
                agroup_recordcontainer: agroup_recordcontainer,
                uploadedFilesStore: this.uploadedFilesStore
            }, this.sidebar]
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
                    this.aboutdeadline = this.sidebar.add({
                        xtype: 'panel',
                        title: 'About this deadline',
                        html: record.data.text,
                        style: 'white-space: pre-line',
                        bodyPadding: 10
                    });
                }
            }
        });
    },

    onAddToUploadFilesStore: function(store, records, index) {
        if(index === 0) {
            this.sidebar.insert(0, {
                title: 'Uploaded files',
                xtype: 'grid',
                store: this.uploadedFilesStore,
                hideHeaders: true,
                columns: [{header: 'Filename', flex: 1, dataIndex: 'filename'}]
            });
            if(this.aboutdeadline) {
                this.aboutdeadline.collapse();
            }
        }
    }
});
