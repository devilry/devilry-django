Ext.define('devilry.administrator.studentsmanager.AddDeliveriesMixin', {
    //requires: [
        //'devilry.student.FileUploadPanel'
        //'devilry.administrator.studentsmanager.LocateGroup'
    //],

    deliveryTypes: {
        TYPE_ELECTRONIC: 0,
        TYPE_NON_ELECTRONIC: 1,
        TYPE_ALIAS: 2
    },

    //onPreviouslyApproved: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(1);
        //if(this.noneSelected()) {
            //this.onNotSingleSelected();
            //return;
        //}
        //var groupRecord = this.getSelection()[0];
        //console.log(groupRecord);

        ////this.assignmentgroupPrevApprovedStore.proxy.extraParams.filters = Ext.JSON.encode([{
            ////field: 'parentnode__parentnode__parentnode',
            ////comp: 'exact',

        //Ext.widget('window', {
            //width: 800,
            //height: 700,
            //modal: true,
            //maximizable: true,
            //layout: 'fit',
            //title: 'Select previously approved group',
            //items: {
                //xtype: 'locategroup',
                //store: this.assignmentgroupPrevApprovedStore,
                //groupRecord: groupRecord
            //}
        //}).show();

        ////this.createDeliveryForGroup(groupRecord, this.deliveryTypes.TYPE_ELECTRONIC);
        ////this.refreshStore();
    //},

    onCreateDummyDelivery: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var groupRecord = this.getSelection()[0];
        this.createDeliveryForGroup(groupRecord, this.deliveryTypes.TYPE_ELECTRONIC);
        this.refreshStore();
    },

    /**
     * @private
     */
    createDeliveryForGroup: function(groupRecord, deliveryType) {
        var delivery = Ext.create('devilry.apps.administrator.simplified.SimplifiedDelivery', {
            successful: true,
            deadline: groupRecord.data.latest_deadline_id,
            delivery_type: deliveryType
            //alias_delivery
        });
        delivery.save();
    }
});
