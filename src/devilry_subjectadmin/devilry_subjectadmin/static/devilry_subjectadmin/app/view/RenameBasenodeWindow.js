/**
 * A window for editing the short_name and long_name attributes of a BaseNode.
 * */
Ext.define('devilry_subjectadmin.view.RenameBasenodeWindow', {
    extend: 'Ext.window.Window',
    cls: 'devilry_rename_basenode_window bootstrap',
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.form.ErrorUtils',
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.CancelButton',
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.SaveButton',
        'devilry_subjectadmin.utils.BaseNodeHelp'
    ],
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    /**
     * @cfg {Object} basenodeRecord (required)
     */

    _apply_template: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
    },

    initComponent: function() {
        var title = this._apply_template(gettext('Rename {something}'), {
            something: this.basenodeRecord.get('short_name')
        });
        this.originalShortname = this.basenodeRecord.get('short_name');
        this.originalLongname = this.basenodeRecord.get('long_name');
        Ext.apply(this, {
            layout: 'fit',
            width: 600,
            height: 370,
            closable: false,
            modal: true,
            title: title,
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
                    name: "short_name",
                    fieldLabel: gettext('Short name'),
                    xtype: 'textfield',
                    allowBlank: false,
                    value: this.originalShortname,
                    listeners: {
                        scope: this,
                        render: function(field) {
                            Ext.defer(function() {
                                field.focus();
                            }, 300);
                        }
                    }
                }, {
                    xtype: 'formhelp',
                    html: devilry_subjectadmin.utils.BaseNodeHelp.getShortNameHelp(),
                    margin: '5 0 0 0'
                }, {
                    name: "long_name",
                    fieldLabel: gettext('Long name'),
                    value: this.originalLongname,
                    xtype: 'textfield',
                    allowBlank: false,
                    margin: '10 0 0 0'
                }, {
                    xtype: 'formhelp',
                    html: devilry_subjectadmin.utils.BaseNodeHelp.getLongNameHelp(),
                    margin: '5 0 0 0'
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
                    xtype: 'savebutton',
                    formBind: true,
                    listeners: {
                        scope: this,
                        click: this._onSave
                    }
                }],
                listeners: {
                    scope: this,
                    render: this._onRenderForm
                }
            }
        });
        this.callParent(arguments);

        this.mon(this.basenodeRecord.proxy, {
            scope:this,
            exception: this._onProxyError
        });
    },

    _getForm: function() {
        return this.down('form').getForm();
    },
    _getFormPanel: function() {
        return this.down('form');
    },

    _onRenderForm: function() {
        var form = this._getForm();
        form.loadRecord(this.basenodeRecord);

        this.down('form').keyNav = Ext.create('Ext.util.KeyNav', this.down('form').el, {
            enter: this._onSave,
            scope: this
        });
    },

    _getMaskElement: function() {
        return this.down('form');
    },

    _onSave: function() {
        var form = this._getForm();
        var values = form.getValues();
        var newShortname = values.short_name;
        var newLongname = values.long_name;
        if(this.originalShortname != newShortname || this.originalLongname != newLongname) {
            var basenodeRecord = this.basenodeRecord;
            form.updateRecord(basenodeRecord);
            this._getMaskElement().setLoading(gettext('Saving') + ' ...');
            basenodeRecord.save({
                scope: this,
                success: this._onSaveSuccess
                //failure: this._onSaveFailure
            });
        } else {
            this._close();
        }
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        var alertmessagelist = this.down('alertmessagelist');
        alertmessagelist.removeAll();
        this.handleProxyError(alertmessagelist, this._getFormPanel(), response, operation);
    },

    _unmask: function() {
        this._getMaskElement().setLoading(false);
    },

    _onSaveSuccess: function() {
        this._unmask();
        this._close();
    },

    /** We reload the page on close even when there is no changes, because we
     * do not track if the cancel button was clicked after a failed save or
     * not, and failed save leaves the record changed. */
    _close: function() {
        window.location.reload();
    }
});
