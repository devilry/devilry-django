/**
 * A dialog that we use to confirm deleting something.
 * */
Ext.define('devilry_extjsextras.ConfirmDeleteDialog', {
    extend: 'Ext.window.Window',
    cls: 'devilry_confirmdeletedialog bootstrap',
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.CancelButton',
        'devilry_extjsextras.DeleteButton'
    ],

    width: 350,
    height: 230,

    /**
     * @cfg {string} required_confirm_text (optional)
     * Defaults to ``DELETE``.
     */
    required_confirm_text: gettext('DELETE'),

    /**
     * @cfg {string} short_description (required)
     * Short description of what you are deleting (normally the name of the item).
     */

    /**
     * @cfg {string} helptpl (optional)
     * A Ext.XTemplate template string. Defaults to a useful localized message,
     * however it can be overridden.  Can use ``required_confirm_text`` and
     * ``short_description`` as template variables.
     */
    helptpl: [
        '<p>',
            gettext('Type {required_confirm_text} in the field below to confirm that you really intend to delete {short_description}.'),
        '</p>'
    ],

    _apply_template: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
    },

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when delete is confirmed.
             * @param dialog This confirm dialog.
             * */
            "deleteConfirmed" : true
        });

        var short_helptext = this._apply_template(gettext('Write "{something}"'), {
            something: this.required_confirm_text
        });

        Ext.apply(this, {
            layout: 'fit',
            closable: false,
            modal: true,
            title: this._apply_template(gettext('Delete {something}?'), {
                something: this.short_description
            }),
            items: {
                xtype: 'form',
                bodyPadding: 20,
                autoScroll: true,
                border: 0,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    margin: {bottom: 5},
                    cls: 'bootstrap',
                    tpl: this.helptpl,
                    data: {
                        short_description: this.short_description,
                        required_confirm_text: this.required_confirm_text
                    }
                }, {
                    name: "confirm_text",
                    xtype: 'textfield',
                    regex: new RegExp('^' + this.required_confirm_text + '$'),
                    invalidText: short_helptext,
                    allowBlank: false,
                    listeners: {
                        scope: this,
                        render: function(field) {
                            Ext.defer(function() {
                                field.focus();
                            }, 200);
                        }
                    }
                }],
                buttons: ['->', {
                    xtype: 'cancelbutton',
                    listeners: {
                        scope: this,
                        click: function() {
                            this._close();
                        }
                    }
                }, {
                    xtype: 'deletebutton',
                    formBind: true,
                    listeners: {
                        scope: this,
                        click: this._onDelete
                    }
                }],
                listeners: {
                    scope: this,
                    render: this._onRenderForm
                }
            }
        });
        this.callParent(arguments);
    },

    _getForm: function() {
        return this.down('form').getForm();
    },
    getFormPanel: function() {
        return this.down('form');
    },

    _onRenderForm: function() {
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onDelete,
            scope: this
        });
    },

    _onDelete: function() {
        var form = this._getForm();
        if(form.isValid()) {
            this.fireEvent('deleteConfirmed', this)
        }
    },

    _close: function() {
        this.close();
    }
});
