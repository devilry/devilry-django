Ext.define('devilry_subjectadmin.view.managestudents.ChooseTagsPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.choosetagspanel',
    cls: 'devilry_subjectadmin_choosetagspanel',

    layout: 'fit',
    border: false,
    frame: false,

    requires: [
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.PrimaryButton'
    ],

    /**
     * @cfg {String} [buttonText]
     */

    /**
     * @cfg {bool} [allowNoTags]
     */
    allowNoTags: false,

    inputFieldType: 'textarea', // NOTE: textarea seems to be the best choice if we are going to use the same for single and multiple groups.

    initialValue: undefined,

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            'savetags',
            'cancel'
        );
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: {
                xtype: 'form',
                bodyPadding: 10,
                listeners: {
                    scope: this,
                    render: this._onRenderFormPanel
                },
                layout: 'anchor',
                items: [{
                    anchor: '100%',
                    xtype: this.inputFieldType,
                    name: 'tags',
                    allowBlank: this.allowNoTags,
                    emptyText: pgettext('tagsexample', 'Example: group3, needs_extra_help'),
                    regex: new RegExp('^[a-zA-Z0-9_, -]+$'),
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
                    anchor: '100%',
                    html: [
                        gettext('Type tags separated by comma (,)'),
                        gettext('A tag can contain a-z, A-Z, 0-9 and "_".')
                    ].join('. ')
                }],
                buttons: [{
                    xtype: 'button',
                    itemId: 'cancelButton',
                    cls: 'choosetags_cancelbutton',
                    text: gettext('Cancel'),
                    listeners: {
                        scope: this,
                        click: this._onCancel
                    }
                }, {
                    xtype: 'primarybutton',
                    itemId: 'saveTags',
                    cls: 'choosetags_savebutton',
                    formBind: true,
                    text: this.buttonText,
                    listeners: {
                        scope: this,
                        click: this._onSave
                    }
                }]
            }
        });
        this.on('show', this._onShow, this);
        this.callParent(arguments);
    },

    _getParsedValueAsArray: function() {
        var form = this.down('form').getForm();
        var tags = form.getFieldValues().tags.split(/\s*,\s*/);
        var nonEmptyTags = Ext.Array.filter(tags, function(tag) {
            return tag !== '';
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
    },

    _onCancel: function() {
        this.fireEvent('cancel', this);
    },

    /** Clear the tags input field. */
    setValue: function(value) {
        this.down(this.inputFieldType).setValue(value);
    },

    setInitialValue: function(initialValue) {
        this.initialValue = initialValue;
    },

    _onShow: function() {
        if(typeof this.initialValue === 'undefined') {
            throw "this.initialValue has not been set. It must be set using setInitialValue() before showing the ChooseTagsPanel.";
        }
        this.setValue(this.initialValue);
        this.down(this.inputFieldType).focus();
    }
});
