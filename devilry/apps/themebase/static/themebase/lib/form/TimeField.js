Ext.define('themebase.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.themebase-timefield',
    cls: 'themebase-timefield',
    format: dtranslate('i18n.timeformat', 'H:i'),
    increment: 180
});
