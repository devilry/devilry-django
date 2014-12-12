Ext.define('devilry_extjsextras.form.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.devilry_extjsextras_datefield',
    cls: 'devilry_extjsextras_datefield',
    format: pgettext('extjs date input format', 'Y-m-d')
});
