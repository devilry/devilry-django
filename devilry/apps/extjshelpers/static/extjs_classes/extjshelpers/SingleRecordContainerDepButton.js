/** A button that has a load mask while a SingleRecordContainer loads. */
Ext.define('devilry.extjshelpers.SingleRecordContainerDepButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.singlerecordcontainerdepbutton',

    config: {
        singlerecordcontainer: undefined
    },

    listeners: {
        afterrender: function(button) {
            if(!this.singlerecordcontainer.record) {
                this.singlerecordcontainer.on('setRecord', function() {
                    button.getEl().unmask();
                });
                button.getEl().mask('Loading');
            }
        }
    }
});
