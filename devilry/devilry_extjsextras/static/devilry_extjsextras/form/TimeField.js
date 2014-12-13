Ext.define('devilry_extjsextras.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.devilry_extjsextras_timefield',
    cls: 'devilry_extjsextras_timefield',
    format: pgettext('extjs time input format', 'H:i'),
    increment: 30,
    requires: [
        'devilry_extjsextras.form.TimeFieldPicker'
    ],

    createPicker: function() {
        var picker;
        this.listConfig = Ext.apply({
            xtype: 'devilry_extjsextras_timefieldpicker',
            selModel: {
                mode: 'SINGLE'
            },
            cls: undefined,
            minValue: this.minValue,
            maxValue: this.maxValue,
            increment: this.increment,
            format: this.format,
            maxHeight: this.pickerMaxHeight
        }, this.listConfig);
        picker = this.callParent();
        this.store = picker.store;
        return picker;
    }
});
