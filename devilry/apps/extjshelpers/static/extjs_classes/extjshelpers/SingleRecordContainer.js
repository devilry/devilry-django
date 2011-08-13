/**
 * Container of a single ``Ext.data.Model`` record, with event listener which
 * fires then the contained record changes.
 */
Ext.define('devilry.extjshelpers.SingleRecordContainer', {
    extend: 'Ext.util.Observable',

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when setRecord is called.
             * @param singlerecordontainer The SingleRecordContainer that fired the event.
             */
            'setRecord');
        this.callParent([config]);
    },

    /**
     * Set the record and fire the _setRecord_ event.
     */
    setRecord: function(record) {
        this.record = record;
        this.fireEvent('setRecord', this);
    },

    /**
     * Fire the setRecord event to with the current record (used to refresh
     * views after changing the current record).
     */
    fireSetRecordEvent: function() {
        this.fireEvent('setRecord', this);
    }
});
