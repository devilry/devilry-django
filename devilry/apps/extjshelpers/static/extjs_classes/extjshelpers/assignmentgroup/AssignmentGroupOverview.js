Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 1000,
    height: 800,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeliveryInfo',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo'
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
        * AssignmentGroup id. (Required).
        */
        assignmentgroupid: undefined,

        /**
         * @cfg {Ext.data.Model} AssignmentGroup model. (Required).
         */
        assignmentgroupmodel: undefined,

        /**
         * @cfg {Ext.data.Model} Delivery model. (Required).
         */
        deliverymodel: undefined,

        /**
         * @cfg {Ext.data.Store} Deadline store. (Required).
         * _Note_ that ``deadlinestore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeadlineListing}.
         */
        deadlinestore: undefined,

        /**
         * @cfg {Ext.data.Store} FileMeta store. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo}.
         */
        filemetastore: undefined,

        /**
         * @cfg {Ext.data.Store} FileMeta store. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}.
         */
        staticfeedbackstore: undefined,

        /**
         * @cfg
         * Enable creation of new feedbacks? Defaults to ``false``.
         *
         * When this is ``true``, the authenticated user still needs to have
         * permission to POST new feedbacks for the view to work.
         */
        canExamine: false
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
                //titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [{
                    xtype: 'assignmentgroupinfo',
                    assignmentgroupid: this.assignmentgroupid,
                    deliverymodel: this.deliverymodel,
                    deadlinestore: this.deadlinestore
                }]
            }, {
                region: 'center',
                id: this.centerAreaId,
                items: []
            }],
        });
        this.callParent(arguments);


        this.assignmentgroupmodel.load(this.assignmentgroupid, {
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
        this.deliverymodel.load(deliveryid, {
            scope: me,
            success: me.setDelivery
        });
    },

    setDelivery: function(deliveryrecord) {
        if(deliveryrecord.data.deadline__assignment_group == this.assignmentgroupid) { // Note that this is not for security (that is handled on the server, however it is to prevent us from showing a delivery within the wrong assignment group (which is a bug))
            var centerArea = Ext.getCmp(this.centerAreaId);
            centerArea.removeAll();
            centerArea.add({
                xtype: 'deliveryinfo',
                assignmentid: this.assignmentid,
                delivery: deliveryrecord.data,
                filemetastore: this.filemetastore,
                staticfeedbackstore: this.staticfeedbackstore,
                canExamine: this.canExamine
            });
        } else {
            var errormsg = Ext.String.format(
                'Invalid deliveryid: {0}. Must be a delivery made by AssignmentGroup: {1}',
                deliveryrecord.id,
                this.assignmentgroupid);
            console.error(errormsg);
        }
    },

    handleNoDeliveryInQuerystring: function() {
        console.log('no delivery selected');
    }
});
