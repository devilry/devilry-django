Ext.define('devilry.extjshelpers.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 800,
    height: 600,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.DeliveryInfo',
        //'devilry.extjshelpers.StaticFeedbackInfo',
        'devilry.extjshelpers.StaticFeedbackEditableInfo',
        'devilry.extjshelpers.StaticFeedbackGrid'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{deadline__assignment_group__parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{deadline__assignment_group__parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{deadline__assignment_group__parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
        * @cfg
        * RestfulSimplifiedFileMeta store. __Required__.
        */
        filemetastoreid: undefined,
        deliveryid: undefined,
        deliverymodelname: undefined,
        staticfeedbackstoreid: undefined
    },

    initFeedbackComponent: function() {
        var staticfeedbackstore = Ext.data.StoreManager.lookup(this.staticfeedbackstoreid);
        //this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackInfo', {
        this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackEditableInfo', {
            store: staticfeedbackstore
        });

        var me = this;
        this.feedbackInfo.addListener('clickNewFeedback', function() {
            var assignmentid = me.delivery.deadline__assignment_group__parentnode;
            me.setCenterAreaContent({
                xtype: 'container',
                loader: {
                    url: Ext.String.format('/gradeeditors/load-grade-editor/{0}', assignmentid),
                    renderer: 'component',
                    autoLoad: true,
                    loadMask: true
                }
            });
        });
    },

    initComponent: function() {
        var me = this;
        this.centerAreaId = this.id + '-center';
        this.initFeedbackComponent();
        

        var mainHeader = Ext.create('Ext.Component');
        var deliveryInfo = Ext.create('devilry.extjshelpers.DeliveryInfo', {
            filemetastore: Ext.data.StoreManager.lookup(this.filemetastoreid)
        });

        Ext.apply(this, {
            items: [{
                region: 'north',
                height: 66,
                xtype: 'container',
                items: [mainHeader]
            }, {
                region: 'center',
                id: this.centerAreaId,
                items: [this.feedbackInfo]
            }, {
                region: 'west',
                width: 220,
                xtype: 'panel',
                collapsible: true,   // make collapsible
                titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [deliveryInfo]
            }],
        });
        this.callParent(arguments);

        Ext.ModelManager.getModel(this.deliverymodelname).load(this.deliveryid, {
            success: function(deliveryrecord) {
                deliveryInfo.setDelivery(deliveryrecord.data);
                mainHeader.update(me.headingTpl.apply(deliveryrecord.data));
                me.delivery = deliveryrecord.data;
                me.feedbackInfo.showNewFeedbackButton();
            }
        });
    },

    setCenterAreaContent: function(content) {
        var centerArea = Ext.getCmp(this.centerAreaId);
        centerArea.removeAll();
        centerArea.add(content);
    }
});
