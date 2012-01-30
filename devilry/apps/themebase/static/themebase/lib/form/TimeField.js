Ext.define('themebase.form.TimeField', {
    extend: 'Ext.form.field.Time',
    alias: 'widget.themebase-timefield',
    format: dtranslate('themebase.timeformat', 'H:i')
});
