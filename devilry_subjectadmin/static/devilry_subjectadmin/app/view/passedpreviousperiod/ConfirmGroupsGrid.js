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
            dataIndex: 'newfeedback_points',
            text: gettext('Grade'),
            flex: 4,
            menuDisabled: true,
            renderer: this._renderGradeColumn,
            sortable: false,
            editor: this._getEditor()
        });
    },

    _getEditor:function (widget) {
        return {
            allowBlank: false,
            xtype: 'textfield'
        };
    },

    _renderGradeColumn: function(value, unused2, record) {
        var oldgroup = record.get('oldgroup');

        var grade = gettext('Passed');
        if(oldgroup !== null) {
            grade = oldgroup.grade;
        }
        var displayValue = Ext.String.format(
            '<span class="text-success">{0}</span>',
            grade);

        if(oldgroup === null) {
            return displayValue;
        } else {
            var autodetectedMsg = gettext('Autodetected');
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
