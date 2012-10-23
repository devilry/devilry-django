Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlines_deadline',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadline',
    collapsible: true,
    collapsed: true,
    animCollapse: false,
    //hideCollapseTool: true,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.model.Group',
        'devilry_subjectadmin.view.bulkmanagedeadlines.GroupsInDeadlineGrid',
        'devilry_subjectadmin.view.bulkmanagedeadlines.EditDeadlineForm',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.DeleteButton'
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
            '<span class="linklike">',
                '<em class="deadline_label">{deadline_term}</em>: ',
                '<span class="deadline">{deadline_formatted}</span>',
            '</span>',
            '<tpl if="in_the_future">',
                '<span class="success"> ({offset_from_now})</span>',
            '<tpl else>',
                '<span class="danger"> ({offset_from_now})</span>',
            '</tpl>',
        '</div>',
        '<div class="metadata">',
            '<small><em>{groups_term}</em>: {groupcount}</small>',
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
                interpolate(gettext('This %(deadline_term)s has no text. Use the edit button if you want to set a text.'), {
                    deadline_term: gettext('deadline')
                }, true),
            '</small></p>',
        '</tpl>'   
    ],

    groupsHeaderTpl: [
        '<h2 class="oneline_ellipsis">',
            gettext('Groups'),
            ' <small>- ',
                interpolate(gettext('%(Students_term)s are organized in %(groups_term)s, even when they work alone'), {
                    Students_term: gettext('Students'),
                    groups_term: gettext('groups')
                }, true),
            '</small>',
        '</h2>',
        '<p class="muted"><small>',
            interpolate(gettext('Select a %(group_term)s to view or edit it in the group manager.'), {
                group_term: gettext('group')
            }, true),
        '</small></p>'
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
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                groups_term: gettext('Groups'),
                groupcount: this.deadlineRecord.get('groups').length,
                text_title: gettext('About this deadline'),
                text: this.deadlineRecord.formatTextOneline(),
                in_the_future: this.deadlineRecord.get('in_the_future'),
                offset_from_now: this.deadlineRecord.formatOffsetFromNow()
            }),
            items: [{
                xtype: 'bulkmanagedeadlines_editdeadlineform',
                margin: '0 0 40 0',
                hidden: true
            }, {
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
                    items: [{
                        xtype: 'primarybutton',
                        itemId: 'editDeadlineButton',
                        width: 180,
                        margin: '0 0 10 0',
                        text: gettext('Edit/move'),
                        listeners: {
                            scope: this,
                            click: this._onEdit
                        }
                    }, {
                        xtype: 'deletebutton',
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
                    xtype: 'box',
                    columnWidth: 1,
                    padding: '0 0 0 30',
                    hidden: true
                    //html: 'TODO: filter groups'
                }]
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
