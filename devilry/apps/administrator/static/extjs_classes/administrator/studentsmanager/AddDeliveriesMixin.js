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
        
        var msg = Ext.create('Ext.XTemplate',
            '<p>Are you sure you want to create a dummy delivery for <em>',
            '    <tpl if="name">',
            '        {name}: ',
            '    </tpl>',
            '    <tpl for="candidates__identifier">',
            '        {.}<tpl if="xindex &lt; xcount">, </tpl>',
            '    </tpl>',
            '</em>?',
            '<tpl if="number_of_deliveries &gt; 0">',
            '   <p><strong>WARNING:</strong> One usually only creates dummy deliveries for groups with no ',
            '   deliveries, however this group has <strong>{number_of_deliveries}</strong> deliveries.</p>',
            '</tpl>'
        );
        var me = this;
        Ext.MessageBox.show({
            title: 'Confirm that you want to create dummy delivery',
            msg: msg.apply(groupRecord.data),
            animateTarget: this.deletebutton,
            buttons: Ext.Msg.YESNO,
            icon: (groupRecord.data.number_of_deliveries>0? Ext.Msg.WARNING: Ext.Msg.QUESTION),
            fn: function(btn) {
                if(btn == 'yes') {
                    me.createDummyDeliveryForSelected(groupRecord);
                }
            }
        });
    },

    /**
     * @private
     */
    createDummyDelivery: function(groupRecord) {
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
