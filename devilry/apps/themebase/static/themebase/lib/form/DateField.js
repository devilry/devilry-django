Ext.define('themebase.form.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.themebase-datefield',
    cls: 'themebase-datefield',
    format: dtranslate('i18n.dateformat', 'Y-m-d')
});
