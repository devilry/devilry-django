Ext.define('devilry.extjshelpers.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 1000,
    height: 800,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.DeliveryInfo',
        'devilry.extjshelpers.AssignmentGroupInfo',
        'devilry.extjshelpers.StaticFeedbackEditableInfo',
        'devilry.extjshelpers.StaticFeedbackGrid'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
        * @cfg
        * AssignmentGroup id.
        */
        assignmentgroupid: undefined
    },

    initFeedbackComponent: function() {
        var staticfeedbackstoreid = 'devilry.apps.examiner.simplified.SimplifiedStaticFeedbackStore';
        var staticfeedbackstore = Ext.data.StoreManager.lookup(staticfeedbackstoreid);
        //this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackInfo', {
        this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackEditableInfo', {
            store: staticfeedbackstore,
            deliveryid: 16
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
        

        this.mainHeader = Ext.create('Ext.Component');
        var filemetastoreid = 'devilry.apps.examiner.simplified.SimplifiedFileMetaStore';
        this.deliveryInfo = Ext.create('devilry.extjshelpers.DeliveryInfo', {
            filemetastore: Ext.data.StoreManager.lookup(filemetastoreid)
        });

        Ext.apply(this, {
            items: [{
                region: 'north',
                height: 66,
                xtype: 'container',
                items: [this.mainHeader]
            }, {
                region: 'west',
                width: 220,
                xtype: 'panel',
                collapsible: true,   // make collapsible
                titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [{
                    xtype: 'assignmentgroupinfo'
                }]
            }, {
                region: 'center',
                id: this.centerAreaId,
                items: [this.deliveryInfo, this.feedbackInfo]
            }],
        });
        this.callParent(arguments);


        var assignmentgroupmodel = Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedAssignmentGroup');
        assignmentgroupmodel.load(this.assignmentgroupid, {
            scope: me,
            success: me.onLoadAssignmentGroup
        });
    },

    onLoadAssignmentGroup: function(assignmentgrouprecord) {
        assignmentgroup = assignmentgrouprecord.data;
        this.mainHeader.update(this.headingTpl.apply(assignmentgroup));
        var assignmentid = assignmentgroup.parentnode;
        this.feedbackInfo.showNewFeedbackButton(assignmentid);
        var query = Ext.Object.fromQueryString(window.location.search);
        this.loadDelivery(query.deliveryid);
    },

    loadDelivery: function(deliveryid) {
        var me = this;
        Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery').load(deliveryid, {
            scope: me,
            success: me.onLoadDelivery
        });
    },

    onLoadDelivery: function(deliveryrecord) {
        this.deliveryInfo.setDelivery(deliveryrecord.data);
        this.delivery = deliveryrecord.data;
    },

    setCenterAreaContent: function(content) {
        var centerArea = Ext.getCmp(this.centerAreaId);
        centerArea.removeAll();
        centerArea.add(content);
    }
});
