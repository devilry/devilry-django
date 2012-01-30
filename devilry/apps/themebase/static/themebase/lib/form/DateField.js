Ext.define('themebase.form.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.themebase-datefield',
    format: dtranslate('themebase.dateformat', 'Y-m-d')
});
