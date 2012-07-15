Ext.define('devilry_extjsextras.EditableSidebarBox', {
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
        text: gettext('Loading...')
    },

    /**
     * @cfg {String} buttontext (optional)
     * Button text. Defaults to "Edit" (translated).
     */
    buttonText: pgettext('uibutton', 'Edit'),

    /**
     * @cfg {object} buttonListeners
     * Listeners for the button.
     */
    buttonListeners: {},

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
                cls: 'bootstrap',
                padding: {top: 3},
                columnWidth: 1,
                html: ''
            }, {
                xtype: 'button',
                scale: 'medium',
                margin: {left: 15},
                width: 70,
                listeners: this.buttonListeners,
                text: this.buttonText
            }]
        });
        this.callParent(arguments);
        this.updateBody(this.bodyTpl, this.data);
    },

    updateBody: function(bodyTpl, data) {
        var data = data || {};
        var tpl = Ext.create('Ext.XTemplate', Ext.Array.from(bodyTpl))
        this.getComponent('body').update(tpl.apply(data));
    },

    updateTitle: function(title) {
        this.setTitle(title);
    }
});
