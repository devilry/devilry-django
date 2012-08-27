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
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.gradeeditors.GradeEditorModel',
            autoSync: true
        });
        this.addListener('render', this._onRender, this);
        this.callParent(arguments);
    },

    _onRender: function() {
        try {
            this.setLoading(gettext('Loading'));
            this._loadStore();
        } catch(e) {
            Ext.defer(function() {
                this.setLoading(gettext('Loading'));
                this._loadStore();
            }, 500, this)
        }
    },

    _loadStore: function() {
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
        this.setLoading(false);
        this.setValue(this.value);
    },

    onLoadFailure: function() {
        this.setLoading(false);
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: 'Failed to load records',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    }
});
