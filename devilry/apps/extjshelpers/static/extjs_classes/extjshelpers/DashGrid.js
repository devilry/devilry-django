Ext.define('devilry.extjshelpers.DashGrid', {
    extend: 'Ext.Container',

    initComponent: function() {
        this.callParent(arguments);
        this.createStore();
        this.loadStore();
    },

    config: {
        noRecordsMessage: {}
    },

    createStore: function() {
        throw "createStore must be implemented";
    },

    loadStore: function() {
        this.store.load({
            scope: this,
            callback: function(records, operation, success) {
                if(!success || records.length === 0) {
                    var args = {};
                    if(success) {
                        Ext.apply(args, this.noRecordsMessage);
                        Ext.apply(args, {msgcls: 'info'});
                    } else {
                        args = {
                            title: 'Error',
                            msg: "Failed to load. Try re-loading the page.",
                            msgcls: 'error'
                        }
                    }
                    this.add({
                        xtype: 'box',
                        renderTo: 'no-active-assignments-message',
                        html: Ext.create('Ext.XTemplate',
                            '<section class="{msgcls}-small extravisible-small">',
                            '   <h1>{title}</h1>',
                            '   <p>{msg}</p>',
                            '</section>'
                        ).apply(args)
                    });
                } else {
                    this.createBody();
                }
            }
        });
    },

    createBody: function() {
    }
});
