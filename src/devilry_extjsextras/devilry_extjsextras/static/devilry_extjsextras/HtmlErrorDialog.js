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

    /**
     * @cfg {Object} bodyConfig
     * Config arguments for the body of the window. The xtype defaults to
     * ``"box"``, but you can override it in ``bodyConfig``.
     */

    initComponent: function() {
        var bodyConfig = {
        };
        Ext.apply(bodyConfig, this.bodyConfig);
        Ext.apply(this, {
            layout: 'fit',
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
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});
