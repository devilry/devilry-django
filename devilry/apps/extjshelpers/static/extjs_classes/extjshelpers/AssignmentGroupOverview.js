Ext.define('devilry.extjshelpers.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 800,
    height: 600,
    layout: 'border',
    alias: 'widget.examinerfeedback',
    requires: [
        'devilry.extjshelpers.DeliveryInfo',
        'devilry.extjshelpers.StaticFeedbackInfo',
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

    initComponent: function() {
        var me = this;
        //this.centerAreaId = this.id + '-center';
        var staticfeedbackstore = Ext.data.StoreManager.lookup(this.staticfeedbackstoreid);
        this.currentlyShownFeedback = Ext.create('devilry.extjshelpers.StaticFeedbackInfo', {
            store: staticfeedbackstore
        });

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
                items: [me.currentlyShownFeedback]
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
            }
        });
    },

    //setCenterAreaContent: function(content) {
        //var centerArea = Ext.getCmp(this.centerAreaId);
        //centerArea.removeAll();
        //centerArea.add(content);
    //}
});
