Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlines_deadline',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadline',
    collapsible: true,
    collapsed: true,
    animCollapse: false,
    hideCollapseTool: true,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.model.Group',
        'devilry_subjectadmin.view.bulkmanagedeadlines.GroupGrid',
        'devilry_subjectadmin.view.bulkmanagedeadlines.DeadlineForm'
    ],

    /**
     * @cfg {Object} [deadlineRecord]
     */

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment of this deadline.
     */

    headerTpl: [
        '<div class="linklike">',
            '<em class="deadline_label">{deadline_term}</em>: ',
            '<span class="deadline">{deadline_formatted}</span>',
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
        '<h2>',
            gettext('Text'),
            ' <small>- ', gettext('Students see this when they add deliveries'), '</small>',
        '</h2>',
        '<tpl if="text">',
            '<p style="white-space: pre-wrap">{text}</p>',
        '<tpl else>',
            '<p><small>',
                interpolate(gettext('This %(deadline_term)s has no text. Use the edit button if you want to set a text.'), {
                    deadline_term: gettext('deadline')
                }, true),
            '</small></p>',
        '</tpl>'   
    ],

    groupsHeaderTpl: [
        '<h2>',
            gettext('Groups'),
            ' <small>- ',
                interpolate(gettext('%(Students_term)s are organized in %(groups_term)s, even when they work alone'), {
                    Students_term: gettext('Students'),
                    groups_term: gettext('groups')
                }, true),
            '</small>',
        '</h2>',
        '<p><small>',
            interpolate(gettext('Select a %(group_term)s to view and edit it.'), {
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
            'editDeadline'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        var deadline_dateobj = this.deadlineRecord.get('deadline');
        var deadline_formatted = Ext.Date.format(deadline_dateobj, 'Y-m-d H:i:s');
        this.groupsStore = this._createGroupStore();
        Ext.apply(this, {
            itemId: Ext.String.format('deadline-{0}', this.deadlineRecord.get('bulkdeadline_id')),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                groups_term: gettext('Groups'),
                groupcount: this.deadlineRecord.get('groups').length,
                text_title: gettext('Deadline text'),
                text: this.deadlineRecord.formatTextOneline(50)
            }),
            tools: [{
                xtype: 'button',
                text: gettext('Edit/move'),
                scale: 'large',
                //ui: 'primary',
                listeners: {
                    scope: this,
                    click: this._onEdit
                }
            }],
            items: [{
                xtype: 'bulkmanagedeadlines_deadlineform',
                margin: '0 40 40 40',
                hidden: true
            }, {
                xtype: 'box',
                itemId: 'deadlineText',
                cls: 'bootstrap',
                tpl: this.deadlineTextTpl,
                data: {
                    text: this.deadlineRecord.get('text')
                }
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
                    xtype: 'bulkmanagedeadlines_groupgrid',
                    width: 300,
                    assignment_id: this.assignment_id,
                    store: this.groupsStore
                }, {
                    xtype: 'box',
                    columnWidth: 1,
                    padding: '0 0 0 30',
                    html: 'filter groups'
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

    _onEdit: function(button, e) {
        this.fireEvent('editDeadline', this, this.deadlineRecord);

        // NOTE: If this cause problems with IE 8, see:
        // - http://stackoverflow.com/questions/387736/how-to-stop-event-propagation-with-inline-onclick-attribute
        // - http://stackoverflow.com/questions/5963669/whats-the-difference-between-event-stoppropagation-and-event-preventdefault
        e.stopPropagation();
    }
});
