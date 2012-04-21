Ext.define('subjectadmin.view.ActivePeriodsList', {
    extend: 'Ext.form.RadioGroup',
    alias: 'widget.activeperiodslist',
    cls: 'activeperiodslist',
    requires: [
        'Ext.XTemplate'
    ],
    columns: 1,
    vertical: true,

    labelTpl: Ext.create('Ext.XTemplate',
        '{parentnode__short_name}.{short_name}'
    ),

    addPeriod: function(periodRecord, checked) {
        var label = this.labelTpl.apply(periodRecord.data);
        this.add({
            boxLabel: label,
            name: this.name,
            inputValue: periodRecord.get('id'),
            checked: checked
        });
    }
});
