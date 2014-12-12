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
        * A {@link devilry.extjshelpers.SingleRecordContainer} which contains data for the ``tpl``.
        */
        singlerecordontainer: undefined,

        /**
         * @cfg
         * An ``Ext.XTemplate`` which takes the record in ``singlerecordontainer.record.data`` as input.
         */
        tpl: undefined,

        /**
         * @cfg
         * Extra data for the ``tpl``. Applied before the data in
         * ``singlerecordontainer``, so any shared attributed with
         * ``singlerecordontainer.data`` will use the attribute in
         * ``singlerecordontainer.data``.
         */
        extradata: {}
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

    getData: function(data) {
        return data;
    },

    /**
     * @private
     */
    updateBody: function() {
        var data = {};
        Ext.apply(data, this.extradata);
        Ext.apply(data, this.singlerecordontainer.record.data);
        data = this.getData(data);
        this.update(this.tpl.apply(data));
    }
});
