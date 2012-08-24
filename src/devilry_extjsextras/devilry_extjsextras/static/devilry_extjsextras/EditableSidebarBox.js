Ext.define('devilry_extjsextras.EditableSidebarBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.editablesidebarbox',


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
            items: [{
                xtype: 'box',
                itemId: 'title',
                cls: 'bootstrap',
                tpl: '<h4>{title}</h4>',
                data: {
                    title: this.title
                }
            }, {
                xtype: 'container',
                layout: 'column',
                cls: 'bootstrap',
                items: [{
                    xtype: 'box',
                    itemId: 'body',
                    padding: '0 15 0 0',
                    columnWidth: 1,
                    html: ''
                }, {
                    xtype: 'button',
                    scale: 'medium',
                    width: 70,
                    listeners: this.buttonListeners,
                    text: this.buttonText
                }]
            }]
        });
        this.callParent(arguments);
        this.updateBody(this.bodyTpl, this.data);
    },

    updateBody: function(bodyTpl, data) {
        var data = data || {};
        var tpl = Ext.create('Ext.XTemplate', Ext.Array.from(bodyTpl))
        this.down('#body').update(tpl.apply(data));
    },

    updateTitle: function(title) {
        this.down('#title').update({
            title: title
        });
    }
});
