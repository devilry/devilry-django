Ext.define('devilry.tutorialstats.ConfigSelector', {
    requires: 'devilry.tutorialstats.BarChart',
    extend: 'Ext.form.field.ComboBox',

    constructor: function(store, renderTo, chart, editform) {
        this.chart = chart;
        this.editform = editform;
        this.store = store;

        this.callParent([{
            fieldLabel: 'Select statistics config',
            renderTo: renderTo,
            displayField: 'name',
            width: 400,
            labelWidth: 130,
            store: store,
            queryMode: 'local',
            typeAhead: true,
            listeners: {
                scope: this, // Without this, on_select_combo runs within the scope of the object that fired the event!
                select: this.on_select_combo
            }
        }]);

        return this;
    },


    /* When selecting an item in the combobox */
    on_select_combo: function(field, value, options) {
        var data = value[0].data;
        var periodpoints_url = data.periodpoints_url;
        if(periodpoints_url) {
            this.chart.refresh(periodpoints_url);
        }

        var item = store.getById(data.id);
        console.log(item);
        this.editform.getForm().loadRecord(item);
    }
});
