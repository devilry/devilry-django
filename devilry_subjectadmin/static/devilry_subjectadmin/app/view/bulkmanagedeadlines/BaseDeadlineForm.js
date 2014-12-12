Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.BaseDeadlineForm', {
    extend: 'Ext.form.Panel',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadlineform bootstrap',

    requires: [
        'devilry_extjsextras.form.DateTimeField',
        'Ext.form.field.TextArea',
        'Ext.util.KeyNav',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.bulkmanagedeadlines.AllGroupsInAssignmentGrid'
    ],

    bodyPadding: 20,
    layout: 'anchor',

    /**
     * @cfg {string} [assignment_id]
     * Used to generate the students manager url in the createmodeContainer.
     */

    /**
     * @cfg {bool} [saveButtonDisabled=false]
     * Disable the savebutton by default?
     */
    saveButtonDisabled: false,

    initComponent: function() {
        Ext.apply(this, {
            cls: this.cls + ' ' + this.extraCls,
            items: this.getItems(),
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
                disabled: this.saveButtonDisabled,
                cls: 'savedeadlinebutton',
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


    getItems: function() {
        return [{
            xtype: 'alertmessagelist'
        }, {
            xtype: 'box',
            anchor: '100%',
            html: [
                '<h2 class="oneline_ellipsis">',
                    gettext('Deadline'),
                    ' <small>- ', gettext('The time when the deadline expires'), '</small>',
                '</h2>'
            ].join('')
        }, {
            xtype: 'devilry_extjsextras-datetimefield',
            name: 'deadline',
            cls: 'deadlinefield',
            fieldLabel: gettext('Deadline'), // NOTE: we need labels for devilry_extjsextras.ErrorUtils
            hideLabel: true,
            allowBlank: false,
            itemId: 'deadlineField',
            width: 300


        // Text
        }, {
            xtype: 'box',
            margin: '20 0 0 0',
            html: [
                '<h2 class="oneline_ellipsis">',
                    gettext('About this deadline'),
                    ' <small>- ', gettext('Students see this when they add deliveries'), '</small>',
                '</h2>'
            ].join('')
        }, {
            xtype: 'textarea',
            name: 'text',
            anchor: '100%',
            height: 100,
            fieldLabel: gettext('Text'), // NOTE: we need labels for devilry_extjsextras.ErrorUtils
            hideLabel: true,
            resizable: true,
            resizeHandles: 's'
        }];
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
