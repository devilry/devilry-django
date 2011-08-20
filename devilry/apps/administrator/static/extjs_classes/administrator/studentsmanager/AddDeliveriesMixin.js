Ext.define('devilry.administrator.studentsmanager.AddDeliveriesMixin', {
    onCreateDeliveryForGroup: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(0);
        if(this.noneSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var record = this.getSelection()[0];
        var delivery = Ext.create('devilry.apps.administrator.simplified.SimplifiedDelivery', {
            successful: true,
            deadline: record.data.latest_deadline_id,
            delivery_type: 2
            //alias_delivery
        });
        delivery.save();
        console.log(delivery);
        this.refreshStore();
    }
});
