Ext.define('devilry.extjshelpers.DashGrid', {
    extend: 'Ext.Container',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

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
                        autoScroll: true,
                        flex: 1,
                        html: Ext.create('Ext.XTemplate',
                            '<div class="section {msgcls}-small extravisible-small">',
                            '   <h1>{title}</h1>',
                            '   <p>{msg}</p>',
                            '</div>'
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
