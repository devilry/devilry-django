Ext.define('themebase.EditableSidebarBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.editablesidebarbox',
    cls: 'editablesidebarbox',

    requires: [
        'themebase.SidebarTitle'
    ],

    /**
     * @cfg {String} title
     */

    /**
     * @cfg {Array|Ext.XTemplate} tpl
     */
    tpl: ['{text}'],

    /**
     * @cfg {Object} data
     * Initial data for the ``tpl``.
     */
    data: {
        text: dtranslate('themebase.loading')
    },

    /**
     * @cfg {String} buttontext (optional)
     * Button text. Defaults to ``dtranslate('themebase.edit')``.
     */
    buttonText: dtranslate('themebase.edit'),

    initComponent: function() {
        var cssclasses = 'createnewassignmentform form-stacked';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        Ext.apply(this, {
            items: [{
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'sidebartitle',
                    columnWidth: .7,
                    title: this.title
                }, {
                    xtype: 'button',
                    columnWidth: .3,
                    text: this.buttonText
                }]
            }, {
                xtype: 'box',
                tpl: this.tpl
            }]
        });
        this.callParent(arguments);
    },


    updateData: function(config) {
        this.down('box').update(data);
    },

    updateTitle: function(title) {
        this.down('sidebartitle').update(title);
    }
});
