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
     * @cfg {String} [bodyCls='']
     * The css class of the body box.
     */
    bodyCls: '',

    /**
     * @cfg {String} buttontext (optional)
     * Button text. Defaults to "Edit" (translated).
     */
    buttonText: pgettext('uibutton', 'Edit'),

    constructor: function(config) {
        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired when the edit-button is clicked.
             * @param box This EditableSidebarBox.
             */
            'edit'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        var cssclasses = 'editablesidebarbox bootstrap';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                itemId: 'title',
                tpl: [
                    '<h4>',
                        '{title}',
                        '&nbsp;',
                        '&nbsp;',
                        '<a class="edit_link" href="#">(',
                            this.buttonText,
                        ')</a>',
                    '</h4>'
                ],
                data: {
                    title: this.title
                }
            }, {
                xtype: 'box',
                itemId: 'body',
                padding: '0',
                cls: this.bodyCls,
                html: ''
            }],
            listeners: {
                scope: this,
                element: 'el',
                delegate: 'a.edit_link',
                click: function(e) {
                    this.fireEvent('edit', this);
                    e.preventDefault();
                }
            }
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
