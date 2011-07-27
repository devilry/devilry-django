/**
 * View panel bound to a {@link devilry.extjshelpers.SingleRecordContainer}.
 * Kind of like ``Ext.view.View`` only for a single record.
 */
Ext.define('devilry.extjshelpers.SingleRecordView', {
    extend: 'Ext.Component',
    alias: 'widget.singlerecordview',

    config: {
        /**
        * @cfg
        */
        singlerecordontainer: undefined,

        /**
         * @cfg
         * An ``Ext.XTemplate`` which takes the record in ``singlerecordontainer.record.data`` as input.
         */
        tpl: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.callParent(arguments);
        if(this.singlerecordontainer.record) {
            this.updateBody();
        }
        this.singlerecordontainer.addListener('setRecord', this.onSetRecord, this);
    },

    /**
     * @private
     */
    onSetRecord: function(singlerecordontainer) {
        this.updateBody();
    },

    /**
     * @private
     */
    updateBody: function() {
        this.update(this.tpl.apply(this.singlerecordontainer.record.data));
    }
});
