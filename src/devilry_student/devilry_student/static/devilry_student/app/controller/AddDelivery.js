Ext.define('devilry_student.controller.AddDelivery', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'add_delivery.AddDeliveryPanel'
    ],

    refs: [{
        ref: 'addDeliveryPanel',
        selector: 'viewport add_delivery'
    }, {
        ref: 'addDeliveryPanelForm',
        selector: 'viewport add_delivery form'
    }],

    init: function() {
        this.control({
            'viewport add_delivery': {
                render: this._onRender
            },
            'viewport add_delivery fileuploadfield': {
                change: this._onAddFileOnDelivery
            }
        });
    },

    _onRender: function() {
        this.groupInfoRecord = this.getAddDeliveryPanel().groupInfoRecord;
    },

    /////////////////////////////////////////////////////
    // Handle adding a delivery
    /////////////////////////////////////////////////////

    _onAddFileOnDelivery: function() {
        console.log('HEI');
    },


    //_createInitialDelivery: function() {
        //console.log('create');
        //this.getAddDeliveryPanel().setLoading(interpolate(gettext('Initializing %(delivery)s...'), {
            //delivery: gettext('delivery'),
        //}, true));
        //var delivery = Ext.create(this.getDeliveryModel(), {
            //deadline: this._getLatestDeadline().id,
            //id: null,
            //successful: false
        //});
        //delivery.save({
            //scope: this,
            //success: this._onCreateDeliverySuccess,
            //failure: this._onCreateDeliveryFailure
        //});
    //},

    //_onCreateDeliverySuccess: function(deliveryrecord) {
        //console.log('created', deliveryrecord.data);
        //this.deliveryInProgressRecord = deliveryrecord;
        //this.getAddDeliveryPanel().setLoading(false);
        //this._uploadFileToDelivery();
    //},

    //_onCreateDeliveryFailure: function(unused, operation) {
        //this.getAddDeliveryPanel().setLoading(false);
        ////console.log(operation);
        //var message = interpolate(gettext('Could not create %(delivery)s on the selected deadline.'), {
            //delivery: gettext('delivery')
        //}, true);
        //var response = Ext.JSON.decode(operation.response.responseText);
        //if(response && response.items.errormessages) {
            //message = response.items.errormessages.join('. ');
        //}
        //Ext.MessageBox.show({
            //title: gettext('Error'),
            //msg: message,
            //icon: Ext.MessageBox.ERROR,
            //buttons: Ext.MessageBox.OK
        //});
    //},


    //_uploadFileToDelivery: function() {
        //console.log('upload');
        //var form = this.getAddDeliveryPanelForm().getForm();
        //var url = Ext.String.format(
            //'{0}/student/add-delivery/fileupload/{1}',
            //DevilrySettings.DEVILRY_URLPATH_PREFIX, this.groupInfoRecord.get('id')
        //);
        //if(form.isValid()){
            //console.log('valid', this.deliveryInProgressRecord.data);
            //this.getAddDeliveryPanel().setLoading(gettext('Uploading your file ...'));
            //form.submit({
                //url: url,
                //scope: this,
                //params: {deliveryid: this.deliveryInProgressRecord.get('id')},
                //success: this.onAddFileSuccess,
                //failure: this.onAddFileFailure
            //});
        //} else {
            //console.log('invalid');
        //}
    //}
});
