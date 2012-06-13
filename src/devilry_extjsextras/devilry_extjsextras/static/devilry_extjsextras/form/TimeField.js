Ext.define('devilry_extjsextras.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.devilry_extjsextras-timefield',
    cls: 'devilry_extjsextras-timefield',
    format: pgettext('extjs time input format', 'H:i'),
    increment: 180
});
