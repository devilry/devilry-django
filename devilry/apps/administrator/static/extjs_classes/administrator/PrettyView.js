Ext.define('devilry.administrator.PrettyView', {
    extend: 'Ext.panel.Panel',
    cls: 'prettyviewpanel',

    config: {
        /**
         * @cfg
         * URL of the RESTful interface for the view.
         */
        restfulUrl: undefined,

        /**
         * @cfg
         * List of buttons for related actions.
         */
        relatedButtons: undefined,

        /**
         * @cfg
         * List menuitems for plugin actions.
         */
        //pluginItems: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var tbar = ['->', {
            xtype: 'button',
            text: 'Delete',
            listeners: {
                scope: this,
                click: this.onDelete
            }
        }, {
            xtype: 'button',
            text: 'Edit',
            listeners: {
                scope: this,
                click: this.onEdit
            }
        }];

        //if(this.pluginItems) {
            //Ext.Array.insert(tbar, 0, this.pluginItems);
        //}

        if(this.relatedButtons) {
            Ext.Array.insert(tbar, 0, this.relatedButtons);
        }

        Ext.apply(this, {
            tbar: tbar,
            items: [{
            }],
        });
        this.callParent(arguments);
    },

    onEdit: function() {
        console.log('edit');
    },

    onDelete: function() {
        console.log('delete');
    }

});
