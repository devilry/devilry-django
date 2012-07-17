/**
 * A dialog that we use to show longer HTML formatted error messages, which
 * Ext.window.MessageBox is not suited to handle.
 * */
Ext.define('devilry_extjsextras.HtmlErrorDialog', {
    extend: 'Ext.window.Window',
    cls: 'devilry_extjsextras_htmlerrordialog bootstrap',
    alias: 'widget.htmlerrordialog',
    requires: [
        'devilry_extjsextras.OkButton'
    ],

    width: 350,
    height: 250,
    modal: true,
    closable: false,
    bodyPadding: 15,

    /** Forwarded to the body element (an Ext.Component) as ``html``. */
    bodyHtml: undefined,

    /** Forwarded to the body element (an Ext.Component) as ``tpl``. */
    bodyTpl: undefined,

    /** Forwarded to the body element (an Ext.Component) as ``data``. */
    bodyData: undefined,

    /**
     * @cfg {String} title
     * Title, default to localized "Error".
     */
    title: gettext('Error'),

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            autoScroll: true,
            items: {
                xtype: 'box',
                tpl: this.bodyTpl,
                data: this.data,
                html: this.bodyHtml
            },

            buttons: ['->', {
                xtype: 'okbutton',
                listeners: {
                    scope: this,
                    click: function() {
                        this.close();
                    },
                    render: function(button) {
                        Ext.defer(function() {
                            button.focus();
                        }, 150);
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});
