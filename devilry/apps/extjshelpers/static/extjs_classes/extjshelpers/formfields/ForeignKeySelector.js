Ext.define('devilry.extjshelpers.formfields.ForeignKeySelector', {
    extend: 'Ext.form.field.Trigger',
    alias: 'widget.foreignkeyselector',
    requires: [
        'devilry.extjshelpers.formfields.ForeignKeyBrowser'
    ],


    //config: {
        //valueField: 'id',
        //displayTpl: '{id}',
        //emptyText: 'Select something',
        //dropdownTpl: '{id}'
    //},

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.model = Ext.ModelManager.getModel(this.model);
        this.displayTpl = Ext.create('Ext.XTemplate', this.displayTpl);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            text: 'Hello world'
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
                tpl: this.dropdownTpl
            }
        });
        win.show();
        win.alignTo(this, 'bl', [0, 0]);
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

    onSelect: function(record) {
        this.setRecordValue(record);
    }
});
