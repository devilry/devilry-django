Ext.define('devilry_extjsextras.EditableSidebarBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.editablesidebarbox',


    /**
     * @cfg {String} title
     */

    /**
     * @cfg {Array|Ext.XTemplate} bodyTpl
     */
    bodyTpl: ['<p>{text}</p>'],

    /**
     * @cfg {Object} [bodyData]
     * Initial data for the ``bodyTpl``.
     */
    bodyData: {
        text: gettext('Loading') + '...'
    },

    /**
     * @cfg {String} [titleCls='editablesidebarbox_title']
     * The css class of the title box.
     */
    titleCls: 'editablesidebarbox_title',

    /**
     * @cfg {String} [bodyCls='editablesidebarbox_body']
     * The css class of the body box.
     */
    bodyCls: 'editablesidebarbox_body',

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
                cls: this.titleCls,
                tpl: [
                    '<h4>',
                        '{title}',
                        '&nbsp;',
                        '&nbsp;',
                        '<a class="edit_link" href="{editurl}">(',
                            this.buttonText,
                        ')</a>',
                    '</h4>'
                ],
                data: {
                    title: this.title,
                    editurl: '#'
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a.edit_link',
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('edit', this);
                    }
                }
            }, {
                xtype: 'box',
                itemId: 'body',
                padding: '0',
                cls: this.bodyCls,
                tpl: this.bodyTpl,
                data: this.bodyData,
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a',
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('bodyLinkClicked', this, e);
                    }
                }
            }]
        });
        this.callParent(arguments);
        //this.updateBody(this.bodyTpl, this.data);
    },

    updateBody: function(data) {
        this.down('#body').update(data);
    },

    updateText: function(text) {
        this.down('#body').update({
            text: text
        });
    },

    updateTitle: function(title, editurl) {
        if(typeof editurl === 'undefined') {
            editurl = '#';
        }
        this.down('#title').update({
            title: title,
            editurl: editurl
        });
    }
});
