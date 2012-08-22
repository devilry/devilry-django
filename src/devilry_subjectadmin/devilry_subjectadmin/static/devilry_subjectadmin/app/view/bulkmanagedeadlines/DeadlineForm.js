Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlineForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.bulkmanagedeadlines_deadlineform',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadlineform',

    requires: [
        'devilry_extjsextras.form.DateTimeField',
        'Ext.form.field.TextArea',
        'Ext.util.KeyNav',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.AlertMessageList'
    ],

    cls: 'bootstrap',
    bodyPadding: 20,
    layout: 'anchor',

    initComponent: function() {
        Ext.apply(this, {

            // Deadline
            items: [{
                xtype: 'alertmessagelist'
            }, {
                xtype: 'box',
                anchor: '100%',
                html: [
                    '<h2>',
                        gettext('Deadline'),
                        ' <small>- ', gettext('The time when the deadline expires'), '</small>',
                    '</h2>',
                ].join(''),
            }, {
                xtype: 'devilry_extjsextras-datetimefield',
                name: 'deadline',
                fieldLabel: gettext('Deadline'), // NOTE: we need labels for devilry_extjsextras.ErrorUtils
                hideLabel: true,
                itemId: 'deadlineField',
                width: 300


            // Text
            }, {
                xtype: 'box',
                margin: '20 0 0 0',
                name: 'text',
                html: [
                    '<h2>',
                        gettext('Text'),
                        ' <small>- ', gettext('Students see this when they add deliveries'), '</small>',
                    '</h2>',
                ].join(''),
            }, {
                xtype: 'textarea',
                name: 'text',
                anchor: '100%',
                height: 150,
                fieldLabel: gettext('Text'), // NOTE: we need labels for devilry_extjsextras.ErrorUtils
                hideLabel: true,
                resizable: true,
                resizeHandles: 's'
            }],

            buttons: [{
                xtype: 'button',
                text: gettext('Cancel'),
                itemId: 'cancelButton',
                listeners: {
                    scope: this,
                    click: this._onCancel
                }
            }, {
                xtype: 'primarybutton',
                text: gettext('Save'),
                itemId: 'saveDeadlineButton',
                listeners: {
                    scope: this,
                    click: this._onSave
                }
            }]
        });
        this.on('show', this._onShow, this);
        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },


    _onCancel: function() {
        this.fireEvent('cancel', this);
    },
    _onSave: function() {
        this.fireEvent('saveDeadline', this);
    },

    _onRender: function() {
        this.keyNav = Ext.create('Ext.util.KeyNav', this.el, {
            enter: this._onSave,
            scope: this
        });
    },

    _onShow: function() {
        this.down('#deadlineField').focus();
    }
});
