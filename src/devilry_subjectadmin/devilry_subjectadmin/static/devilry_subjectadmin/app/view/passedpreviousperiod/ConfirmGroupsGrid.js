Ext.define('devilry_subjectadmin.view.passedpreviousperiod.ConfirmGroupsGrid', {
    extend: 'devilry_subjectadmin.view.passedpreviousperiod.GridBase',
    alias: 'widget.confirmpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_editpassedpreviousgroupssgrid bootstrap',

    requires: [
        'Ext.grid.plugin.CellEditing'
    ],
    hideHeaders: false,

    /**
     * @cfg {object} [gradeeditor]
     */

    extraInit: function () {
        this.selType = 'cellmodel';
        this.cellEditor = Ext.create('Ext.grid.plugin.CellEditing', {
            clicksToEdit: 1,
            listeners: {
                scope: this,
                beforeedit: this._onBeforeEdit
            }
        });
        this.plugins = [
            this.cellEditor
        ];
        this.columns.push({
            dataIndex: 'newfeedback_shortformat',
            text: gettext('Grade'),
            flex: 4,
            menuDisabled: true,
            renderer: this._renderGradeColumn,
            sortable: false,
            editor: this._getEditor(this.gradeeditor.shortformat.widget)
        });
    },

    _getEditor:function (widget) {
        var editor = {
            allowBlank: false
        };
        if(widget === 'bool') {
            editor.xtype = 'textfield';
            editor.readOnly = true;
        } else if(widget === 'num-of-total') {
            editor.xtype = 'numberfield';
            editor.minValue = 0;
        } else {
            throw Ext.String.format("Unsupported widget: {0}", widget);
        }
        return editor;
    },

    _renderGradeColumn: function(value, unused2, record) {
        var displayValue = value;
        if(this.gradeeditor.shortformat.widget === 'bool') {
            displayValue = Ext.String.format(
                '<span class="text-success">{0}</span>',
                gettext('Passed'));
        }
        var oldgroup = record.get('oldgroup');
        if(oldgroup === null) {
            return displayValue;
        } else {
            var autodetectedMsg;
            if(this.gradeeditor.shortformat.widget === 'bool') {
                autodetectedMsg = gettext('Autodetected');
            } else {
                autodetectedMsg = Ext.String.format('{0}: {1}',
                    gettext('Autodetected'), oldgroup.feedback_shortformat);
            }
            return Ext.String.format(
                '{0} <div class="autodetected"><small class="muted">{1}</small></div>',
                displayValue, autodetectedMsg);
        }
    },

    _onBeforeEdit:function (editor, e) {
        if(this.gradeeditor.shortformat.widget === 'bool') {
            return false; // Can not edit
        }
    }
});