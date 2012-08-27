Ext.define('devilry.gradeeditors.GradeEditorSelector', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.gradeeditorselector',
    cls: 'widget-gradeeditorselector',
    requires: ['devilry.gradeeditors.GradeEditorModel'],

    valueField: 'gradeeditorid',
    displayField: 'title',
    queryMode: 'local',
    editable: false,

    listConfig: {
        getInnerTpl: function() {
            return '<div class="section gradeeditorselector"><div class="important">{title}</div><div class="unimportant">{description}</div></div>';
        }
    },


    initComponent: function() {
        this.loadingFinished = false;
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.gradeeditors.GradeEditorModel',
            autoSync: true
        });
        this.addListener('render', function() {
            Ext.defer(function() {
                if(!this.loadingFinished) {
                    this.setLoading(gettext('Loading'));
                }
            }, 300, this);
        }, this);
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
        this.loadingFinished = true;
        if(this.rendered) {
            this.setLoading(false);
        }
    },

    onLoadFailure: function() {
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: 'Failed to load records',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    }
});
