Ext.define('devilry_subjectadmin.view.passedpreviousperiod.ConfirmGroupsGrid', {
    extend: 'devilry_subjectadmin.view.passedpreviousperiod.GridBase',
    alias: 'widget.confirmpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_editpassedpreviousgroupssgrid bootstrap',

    requires: [
        'Ext.grid.plugin.CellEditing'
    ],
    hideHeaders: false,

//    disableSelection: true,

    extraInit: function () {
        this.columns.push({
            dataIndex: 'feedback_shortformat',
            text: gettext('Grade'),
            flex: 3,
            menuDisabled: true,
            renderer: this._renderGradeCol,
            sortable: false,
            editor: {
                allowBlank: false
            }
        });

        this.selType = 'cellmodel';
        this.plugins = [
            Ext.create('Ext.grid.plugin.CellEditing', {
                clicksToEdit: 1
            })
        ];
    },

    _renderGradeColumn: function(unused, unused2, record) {
        return '';
    }
});