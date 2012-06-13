Ext.define('devilry_extjsextras.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.devilry_extjsextras-timefield',
    cls: 'devilry_extjsextras-timefield',
    format: dtranslate('i18n.timeformat', 'H:i'),
    increment: 180
});
