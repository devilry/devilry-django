Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlines_deadline',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadline',
    bodyCls: 'bulkmanagedeadlines_deadline_body',
    collapsible: true,
    collapsed: true,
    animCollapse: false,
    //hideCollapseTool: true,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.model.Group',
        'devilry_subjectadmin.view.bulkmanagedeadlines.GroupsInDeadlineGrid',
        'devilry_subjectadmin.view.bulkmanagedeadlines.EditDeadlineForm',
        'devilry_subjectadmin.view.managestudents.GroupHelp',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.DeleteButton',
        'devilry_extjsextras.MarkupMoreInfoBox'
    ],

    /**
     * @cfg {Object} [deadlineRecord]
     */

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment of this deadline.
     */

    headerTpl: [
        '<div class="bootstrap">',
            '<small class="deadline_label"><em>', gettext('Deadline'),'</em></small>: ',
            '<strong class="deadline linklike">{deadline_formatted}</strong>',
            '<tpl if="in_the_future">',
                '<span class="text-success"> ({offset_from_now})</span>',
            '<tpl else>',
                '<span class="text-warning"> ({offset_from_now})</span>',
            '</tpl>',
        '</div>',
        '<div class="metadata">',
            '<small><em>', gettext('Groups'), '</em>: {groupcount}</small>',
            '<tpl if="text">',
                '&nbsp;',
                '&nbsp;',
                '&nbsp;',
                '<small><em>{text_title}</em>: {text}</small>',
            '</tpl>',   
        '</div>'
    ],


    deadlineTextTpl: [
        '<h2 class="oneline_ellipsis">',
            gettext('About this deadline'),
            ' <small>- ', gettext('Students see this when they add deliveries'), '</small>',
        '</h2>',
        '<tpl if="text">',
            '<p style="white-space: pre-wrap">{text}</p>',
        '<tpl else>',
            '<p class="muted"><small>',
                gettext('This deadline has no text. Use the edit button if you want to set a text.'),
            '</small></p>',
        '</tpl>'   
    ],

    groupsHeaderTpl: [
        '<h2 class="oneline_ellipsis">',
            gettext('Groups'),
            ' <small>- ',
                gettext('Students are organized in groups, even when they work alone'),
            '</small>',
        '</h2>'
    ],

    groupsHelpTpl: [
        '<p class="muted">',
            gettext('Select a group to view or edit it.'),
            ' {MORE_BUTTON}',
        '</p>',
        '<div {MORE_ATTRS}>',
            '{[devilry_subjectadmin.view.managestudents.GroupHelp.getGroupInfoColHelp()]}',
        '</div>'
    ],

    constructor: function(config) {
        this.initConfig(config);
        this.addEvents(
            /* @event
             * Fired when the edit deadline button is clicked.
             * @param panel This panel
             * @param deadlineRecod The deadline record.
             */
            'editDeadline',

            /* @event
             * Fired when the delete deadline button is clicked.
             * @param panel This panel
             * @param deadlineRecod The deadline record.
             */
            'deleteDeadline'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        var deadline_formatted = this.deadlineRecord.formatDeadline();
        this.groupsStore = this._createGroupStore();
        Ext.apply(this, {
            itemId: Ext.String.format('deadline-{0}', this.deadlineRecord.get('bulkdeadline_id')),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_formatted: deadline_formatted,
                groupcount: this.deadlineRecord.get('groups').length,
                text_title: gettext('About this deadline'),
                text: this.deadlineRecord.formatTextOneline(),
                in_the_future: this.deadlineRecord.get('in_the_future'),
                offset_from_now: this.deadlineRecord.formatOffsetFromNow()
            }),

            layout: 'card',
            items: [{
                xtype: 'container',
                itemId: 'viewDeadline',
                layout: 'anchor',
                defaults: {anchor: '100%'},
                items: [{
                    xtype: 'container',
                    layout: 'column',
                    items: [{
                        xtype: 'box',
                        itemId: 'deadlineText',
                        cls: 'bootstrap',
                        columnWidth: 1,
                        tpl: this.deadlineTextTpl,
                        data: {
                            text: this.deadlineRecord.get('text')
                        }
                    }, {
                        xtype: 'container',
                        width: 180,
                        itemId: 'deadlineButtonContainer',
                        margin: '0 0 0 40',
                        padding: '18 0 0 0', // Line up upper border with first heading
                        items: [{
                            xtype: 'button',
                            scale: 'large',
                            itemId: 'editDeadlineButton',
                            cls: 'edit_deadline_button',
                            width: 180,
                            margin: '0 0 10 0',
                            text: gettext('Edit/move'),
                            listeners: {
                                scope: this,
                                click: this._onEdit
                            }
                        }, {
                            xtype: 'deletebutton',
                            cls: 'delete_deadline_button',
                            itemId: 'deleteDeadlineButton',
                            width: 180,
                            listeners: {
                                scope: this,
                                click: this._onDelete
                            }
                        }]
                    }]
                }, {
                    xtype: 'box',
                    margin: '20 0 0 0',
                    cls: 'bootstrap',
                    tpl: this.groupsHeaderTpl,
                    data: {}
                }, {
                    xtype: 'container',
                    layout: 'column',
                    items: [{
                        xtype: 'bulkmanagedeadlines_groupsindeadlinegrid',
                        width: 300,
                        assignment_id: this.assignment_id,
                        store: this.groupsStore
                    }, {
                        xtype: 'markupmoreinfobox',
                        columnWidth: 1,
                        padding: '0 0 0 30',
                        tpl: this.groupsHelpTpl,
                        data: {}
                        // TODO: filter groups
                    }]
                }]
            }, {
                xtype: 'bulkmanagedeadlines_editdeadlineform',
                itemId: 'editDeadline',
                groupsStore: this.groupsStore,
                margin: '0 0 40 0'
            }]
        });
        this.callParent(arguments);
    },

    _createGroupStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: 'devilry_subjectadmin.model.Group',
            data: this.deadlineRecord.get('groups')
        });
        return store;
    },

    _onEdit: function(button) {
        this.fireEvent('editDeadline', this, this.deadlineRecord);
    },

    _onDelete: function(button) {
        this.fireEvent('deleteDeadline', this, this.deadlineRecord);
    }
});
