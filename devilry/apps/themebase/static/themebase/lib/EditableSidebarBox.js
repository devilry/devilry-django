Ext.define('themebase.EditableSidebarBox', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.editablesidebarbox',

    ui: 'lookslike-parawitheader-panel',
    layout: 'column',

    /**
     * @cfg {String} title
     */

    /**
     * @cfg {Array|Ext.XTemplate} bodyTpl
     */
    bodyTpl: ['{text}'],

    /**
     * @cfg {Object} data
     * Initial data for the ``bodyTpl``.
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
        var cssclasses = 'editablesidebarbox';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        Ext.apply(this, {
            title: this.title,
            items: [{
                xtype: 'box',
                itemId: 'body',
                padding: {top: 3},
                columnWidth: .76,
                html: ''
            }, {
                xtype: 'button',
                columnWidth: .24,
                text: this.buttonText
            }]
        });
        this.callParent(arguments);
        this.updateBody(this.bodyTpl, this.data);
    },

    updateBody: function(bodyTpl, data) {
        var tpl = Ext.create('Ext.XTemplate', bodyTpl)
        this.getComponent('body').update(tpl.apply(data));
    },

    updateTitle: function(title) {
        this.setTitle(title);
    }
});
