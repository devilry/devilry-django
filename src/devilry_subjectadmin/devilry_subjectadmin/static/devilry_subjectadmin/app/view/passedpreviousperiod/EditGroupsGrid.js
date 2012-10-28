Ext.define('devilry_subjectadmin.view.passedpreviousperiod.EditGroupsGrid', {
    extend: 'devilry_subjectadmin.view.passedpreviousperiod.GridBase',
    alias: 'widget.editpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_editpassedpreviousgroupssgrid bootstrap',

    requires: [
        'Ext.grid.plugin.CellEditing',
        'Ext.selection.CellModel'
    ],

    initComponent: function() {
        var cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
            clicksToEdit: 1,
            //errorSummary: false
        });
        Ext.apply(this, {
            selModel: {
                selType: 'cellmodel'
            },
            columns: [{
                dataIndex: 'id',
                flex: 5,
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }, {
                dataIndex: 'id',
                width: 200,
                menuDisabled: true,
                renderer: this.renderCol2,
                sortable: false
            }, {
                dataIndex: 'grade',
                text: Ext.String.format('{0} ({1})', gettext('Grade'), gettext('click cell to edit')),
                flex: 3,
                menuDisabled: true,
                sortable: false,
                editor: {
                    xtype: 'textfield',
                    allowBlank: false
                }
            }, {
                dataIndex: 'comment',
                text: Ext.String.format('{0} ({1})', gettext('Comment'), gettext('click cell to edit')),
                flex: 5,
                menuDisabled: true,
                sortable: false,
                editor: {
                    xtype: 'textarea',
                    height: 40,
                    enterIsSpecial: true,
                    allowBlank: false
                }
            }],
            plugins: [cellEditing]
        });
        this.callParent(arguments);
    }
});
