Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlines_deadline',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadline',
    collapsible: true,
    collapsed: true,
    titleCollapse: true,
    animCollapse: false,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.model.Group',
        'devilry_subjectadmin.view.bulkmanagedeadlines.GroupGrid'
    ],

    /**
     * @cfg {Object} [deadlineRecord]
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
        '<h2>', gettext('Deadline text'), '</h2>',
        '<p style="white-space: pre-wrap">{text}</p>'
    ],

    groupsHeaderTpl: [
        '<h2>',
            gettext('Groups'),
            ' <small>(', gettext('Students'), ')</small>',
        '</h2>',
        '<p><small>',
            interpolate(gettext('Select a %(group_term)s to view and edit it.'), {
                group_term: gettext('group')
            }, true),
        '</small></p>'
    ],

    initComponent: function() {
        var deadline_dateobj = this.deadlineRecord.get('deadline');
        var deadline_formatted = Ext.Date.format(deadline_dateobj, 'Y-m-d h:i:s');
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
            items: [{
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
    }
});
