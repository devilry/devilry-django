Ext.define('devilry.gradeeditors.GradeEditorSelector', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.gradeeditorselector',
    cls: 'widget-gradeeditorselector',
    requires: ['devilry.gradeeditors.GradeEditorModel'],

    valueField: 'gradeeditorid',
    displayField: 'title',
    queryMode: 'local',

    listConfig: {
        getInnerTpl: function() {
            return '<div class="important">{title}</div><div class="unimportant">{description}</div>';
        }
    },


    initComponent: function() {
        this.neverLoaded = true;
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.gradeeditors.GradeEditorModel',
            autoSync: true
        });
        this.callParent(arguments);
        this.store.load({
            scope: this,
            callback: function(records, op, success) {
                if(success) {
                    this.onLoadSuccess(records);
                } else {
                    this.onLoadFailure(records);
                }
            }
        });
    },

    onLoadSuccess: function(records) {
        this.setValue(this.value);
    },

    onLoadFailure: function() {
        console.error('Failed to load records');
    }
});
