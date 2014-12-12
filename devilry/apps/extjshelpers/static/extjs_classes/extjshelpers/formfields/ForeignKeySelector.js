/** Field for selection of foreign key values.
 *
 * **NOTE**: Assumes that the foreign key is a number and that its value is in
 * the ``id`` attribute.
 */
Ext.define('devilry.extjshelpers.formfields.ForeignKeySelector', {
    extend: 'Ext.form.field.Trigger',
    alias: 'widget.foreignkeyselector',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeyBrowser'
    ],

    config: {
        /**
         * @cfg
         * Ext.XTemplate for the selected item.
         */
        displayTpl: '{id}',

        /**
         * @cfg
         * Text to display when field is blank.
         */
        emptyText: 'Select something',

        /**
         * @cfg
         * Ext.XTemplate for items in the dropdown.
         */
        dropdownTpl: '{id}',

        /**
         * @cfg
         * The ``Ext.data.Model`` where the data is located. The model must have a proxy.
         */
        model: undefined,

        /**
         * @cfg
         * Allow empty?
         */
        allowEmpty: false
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.model = Ext.ModelManager.getModel(this.model);
        this.displayTpl = Ext.create('Ext.XTemplate', this.displayTpl);
        this.realValue = '';
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            editable: false,
            listeners: {
                scope: this,
                focus: this.onTriggerClick
            }
        });
        this.callParent(arguments);
    },

    onTriggerClick: function() {
        var win = Ext.create('Ext.window.Window', {
            height: 300,
            width: this.getWidth(),
            modal: true,
            layout: 'fit',
            items: {
                xtype: 'foreignkeybrowser',
                model: this.model,
                foreignkeyselector: this,
                allowEmpty: this.allowEmpty,
                tpl: this.dropdownTpl
            },
            listeners: {
                scope: this,
                show: this._onShowWindow
            }
        });
        win.show();
    },

    _onShowWindow: function(win) {
        try {
            win.alignTo(this, 'bl', [0, 0]);
        } catch(e) {
            Ext.defer(function() {
                win.alignTo(this, 'bl', [0, 0]);
            }, 300, this)
        }
    },
    
    setValue: function(value) {
        var valueType = Ext.typeOf(value);
        if(valueType == 'number') {
            var recordId = value;
            this.model.load(recordId, {
                scope: this,
                success: this.onLoadSuccess,
                failure: this.onLoadFailure
            });
        } else {
            this.callParent([value]);
        }
    },

    getValue: function() {
        return this.realValue;
    },

    getRawValue: function() {
        return this.realValue;
    },

    onLoadSuccess: function(record) {
        this.setRecordValue(record);
    },

    setRecordValue: function(record) {
        this.realValue = record.data.id;
        this.setValue(this.displayTpl.apply(record.data));
    },

    onLoadFailure: function() {
        throw "Failed to load foreign key value.";
    },

    // Triggered by ForeignKeyBrowser.
    onClearValue: function(record) {
        this.realValue = '';
        this.setValue('');
    },

    // Triggered by ForeignKeyBrowser.
    onSelect: function(record) {
        this.setRecordValue(record);
    }
});
