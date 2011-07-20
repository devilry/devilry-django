Ext.define('devilry.extjshelpers.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 1000,
    height: 800,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.DeliveryInfo',
        'devilry.extjshelpers.AssignmentGroupInfo'
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


    initComponent: function() {
        var me = this;
        this.centerAreaId = this.id + '-center';
        this.mainHeader = Ext.create('Ext.Component');

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
                items: []
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
        this.assignmentid = assignmentgroup.parentnode;
        //this.feedbackInfo.showNewFeedbackButton(assignmentid);
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.deliveryid == undefined) {
            this.handleNoDeliveryInQuerystring();
        } else {
            this.loadDelivery(query.deliveryid);
        }
    },

    loadDelivery: function(deliveryid) {
        var me = this;
        Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery').load(deliveryid, {
            scope: me,
            success: me.onLoadDelivery
        });
    },

    onLoadDelivery: function(deliveryrecord) {
        var centerArea = Ext.getCmp(this.centerAreaId);
        centerArea.removeAll();
        centerArea.add({
            xtype: 'deliveryinfo',
            assignmentid: this.assignmentid,
            delivery: deliveryrecord.data
        });
    },

    handleNoDeliveryInQuerystring: function() {
        console.log('no delivery selected');
    }
});
