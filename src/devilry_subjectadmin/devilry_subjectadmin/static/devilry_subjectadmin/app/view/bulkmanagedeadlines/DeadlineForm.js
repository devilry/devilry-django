Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlineForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.bulkmanagedeadlines_deadlineform',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadlineform',

    requires: [
        'devilry_extjsextras.form.DateTimeField',
        'devilry_subjectadmin.utils.UrlLookup',
        'Ext.form.field.TextArea',
        'Ext.util.KeyNav',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.AlertMessageList'
    ],

    cls: 'bootstrap',
    bodyPadding: 20,
    layout: 'anchor',

    /**
     * @cfg {string} [assignment_id]
     * Used to generate the students manager url in the createmodeContainer.
     */

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
                ].join('')
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
                html: [
                    '<h2>',
                        gettext('About this deadline'),
                        ' <small>- ', gettext('Students see this when they add deliveries'), '</small>',
                    '</h2>',
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
            
            // Who to create for? - only shown on create deadline if the assignment already has at least one deadline.
            }, {
                xtype: 'container',
                itemId: 'createmodeContainer',
                hidden: true,
                items: [{
                    xtype: 'box',
                    margin: '20 0 0 0',
                    html: [
                        '<h2>',
                            interpolate(gettext('Add %(deadline_term)s on'), {
                                deadline_term: gettext('deadline')
                            }, true),
                        '</h2>'
                    ].join('')
                }, {
                    xtype: 'radiogroup',
                    anchor: '100%',
                    vertical: true,
                    columns: 1,
                    fieldLabel: interpolate(gettext('Add %(deadline_term)s on'), {
                        deadline_term: gettext('deadline')
                    }, true),
                    hideLabel: true,
                    items: [{
                        boxLabel: interpolate(gettext('%(groups_term)s where active %(feedback_term)s is a failing %(grade_term)s.'), {
                            groups_term: gettext('groups'),
                            grade_term: gettext('grade'),
                            feedback_term: gettext('feedback')
                        }, true),
                        name: 'createmode',
                        inputValue: 'failed',
                        checked: true
                    }, {
                        boxLabel: interpolate(gettext('%(groups_term)s where active %(feedback_term)s is a failing %(grade_term)s, and on %(groups_term)s with no %(feedback_term)s.'), {
                            groups_term: gettext('groups'),
                            grade_term: gettext('grade'),
                            feedback_term: gettext('feedback')
                        }, true),
                        name: 'createmode',
                        inputValue: 'failed-or-no-feedback'
                    }, {
                        boxLabel: interpolate(gettext('%(groups_term)s with no %(deadlines_term)s.'), {
                            groups_term: gettext('groups'),
                            deadlines_term: gettext('deadlines')
                        }, true),
                        name: 'createmode',
                        inputValue: 'no-deadlines'
                    }]
                }, {
                    xtype: 'box',
                    cls: 'bootstrap muted',
                    html: interpolate(gettext('Use the <a href="%(studentsmanager_url)s">students manager</a> to add %(deadlines_term)s to individual %(groups_term)s or custom selections of %(groups_term)s.'), {
                        studentsmanager_url: devilry_subjectadmin.utils.UrlLookup.manageStudents(this.assignment_id),
                        deadlines_term: gettext('deadlines'),
                        groups_term: gettext('groups')
                    }, true)
                }]
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
