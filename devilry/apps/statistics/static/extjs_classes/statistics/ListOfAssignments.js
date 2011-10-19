Ext.define('devilry.statistics.ListOfAssignments', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-listofassignments',
    hideHeaders: true,
    recordTpl: Ext.create('Ext.XTemplate',
        '<tpl for="assignments">',
        '    {.}<tpl if="xindex &lt; xcount"> OR </tpl>',
        '</tpl>'
    ),

    initComponent: function() {
        this.store = Ext.create('Ext.data.ArrayStore', {
            autoDestroy: true,
            idIndex: 0,
            fields: ['assignments']
        });
        this.store.add({
            assignments: ['week1', 'week2']
        })

        Ext.apply(this, {
            columns: [{
                header: 'Assignments', dataIndex: 'assignments', flex: 1,
                renderer: function(value, p, record) {
                    return this.recordTpl.apply({assignments: value});
                }
            }],
            bbar: [{
                xtype: 'button',
                text: 'Add assignment',
                listeners: {
                    scope: this,
                    click: this._onClickAdd
                }
            }]
        });
        this.callParent(arguments);
    },

    _onClickAdd: function() {
        var me = this;
        Ext.Msg.prompt('Assignment(s)', 'Please enter assignment(s):', function(btn, text){
            if(btn == 'ok'){
                var assignments = me._parseAssignmentSpec(text);
                console.log(assignments);
                me._addAssignmentGroupToStore(assignments);
            }
        });
    },

    _parseAssignmentSpec: function(mustPassItemAsStr) {
        return mustPassItemAsStr.split(/\s*,\s*/);;
    },

    _addAssignmentGroupToStore: function(assignments) {
        this.store.add({
            assignments: assignments
        });
    }
});
