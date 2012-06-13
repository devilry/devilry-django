Ext.define('devilry_extjsextras.form.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.devilry_extjsextras-datefield',
    cls: 'devilry_extjsextras-datefield',
    format: dtranslate('i18n.dateformat', 'Y-m-d')
});
