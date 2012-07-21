Ext.define('devilry_subjectadmin.view.managestudents.ChooseTagsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.choosetagswindow',
    cls: 'devilry_subjectadmin_choosetagswindow',

    layout: 'fit',
    closable: true,
    //width: 500,
    //height: 300,
    maximizable: true,
    modal: true,

    requires: [
        'devilry_extjsextras.form.Help'
    ],

    /**
     * @cfg {String} [buttonText]
     */

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            'savetags'
        );
    },

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'form',
                bodyPadding: 20,
                listeners: {
                    scope: this,
                    render: this._onRenderFormPanel
                },
                items: [{
                    xtype: 'textfield',
                    width: 500,
                    name: 'tags',
                    allowBlank: false,
                    emptyText: pgettext('tagsexample', 'Example: group3, needs_extra_help'),
                    regex: new RegExp('^[a-zA-Z0-9_, ]+$'),
                    regexText: gettext('A tag can contain a-z, A-Z, 0-9 and "_".'),
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
                    width: 500,
                    html: [
                        gettext('Type tags separated by comma (,)'),
                        gettext('A tag can contain a-z, A-Z, 0-9 and "_".')
                    ].join('. ')
                }],
                buttons: [{
                    xtype: 'button',
                    scale: 'medium',
                    itemId: 'saveTags',
                    formBind: true,
                    text: this.buttonText,
                    listeners: {
                        scope: this,
                        click: this._onSave
                    }
                }]
            }
        });
        this.callParent(arguments);
    },

    _getParsedValueAsArray: function() {
        var form = this.down('form').getForm();
        var tags = form.getFieldValues().tags.split(/\s*,\s*/);
        var nonEmptyTags = Ext.Array.filter(tags, function(tag) {
            return tag != '';
        });
        return Ext.Array.unique(nonEmptyTags);
    },

    _isValid: function() {
        return this.down('form').getForm().isValid();
    },

    _onRenderFormPanel: function(formpanel) {
        formpanel.keyNav = Ext.create('Ext.util.KeyNav', formpanel.el, {
            enter: this._onSave,
            scope: this
        });
    },

    _onSave: function() {
        if(this._isValid()) {
            this.fireEvent('savetags', this, this._getParsedValueAsArray());
        }
    }
});
