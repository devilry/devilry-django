Ext.define('devilry.extjshelpers.formfields.DateTimeField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.devilrydatetimefield',
    format: 'Y-m-d H:i:s',
    submitFormat: 'Y-m-d\\TH:i:s',
    emptyText: 'YYYY-MM-DD hh:mm:ss'
});
