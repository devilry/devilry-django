Ext.define('devilry_subjectadmin.view.approvedpreviousperiod.SelectAssignmentsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.selectassignmentsgrid',
    cls: 'devilry_subjectadmin_selectassignmentsgrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.GridBigButtonCheckboxModel'
    ],

    store: 'Assignments',
    border: 1,
    frame: false,
    hideHeaders: true,

    col1Tpl: [
        '<div class="assignmentcell assignmentcell_id_{record.id} assignmentcell_shortname_{record.short_name}">',
            '<div class="long_name_box">',
                '<strong class="long_name">{record.long_name}</strong>',
            '</div>',
            '<div class="short_name_box"><small>',
                '<em>', gettext('Short name') ,':</em> ',
                '<small class="short_name">{record.short_name}</small>',
            '</small></div>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
            columns: [{
                dataIndex: 'id',
                flex: 1,
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }],
            tbar: [{
                text: gettext('Select'),
                menu: [{
                    text: gettext('Select all'),
                    listeners: {
                        scope: this,
                        click: this._onSelectAll
                    }
                }, {
                    text: gettext('Deselect all'),
                    listeners: {
                        scope: this,
                        click: this._onDeSelectAll
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    renderCol1: function(unused, unused2, record) {
        return this.col1TplCompiled.apply({
            record: record.data
        });
    },

    _onSelectAll: function() {
        this.getSelectionModel().selectAll();
    },
    _onDeSelectAll: function() {
        this.getSelectionModel().deselectAll();
    }
});
