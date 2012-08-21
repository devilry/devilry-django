Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.DeadlinePanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlines_deadline',
    cls: 'devilry_subjectadmin_bulkmanagedeadlines_deadline',
    collapsible: true,
    collapsed: true,
    titleCollapse: true,
    animCollapse: false,

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

    initComponent: function() {
        var deadline_dateobj = this.deadlineRecord.get('deadline');
        var deadline_formatted = Ext.Date.format(deadline_dateobj, 'Y-m-d h:i:s');
        console.log(this.deadlineRecord.data);

        Ext.apply(this, {
            //itemId: Ext.String.format('deadline-{0}', this.deadline.id),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                deadline_term: gettext('Deadline'),
                deadline_formatted: deadline_formatted,
                groups_term: gettext('Groups'),
                groupcount: this.deadlineRecord.get('groups').length,
                text_title: gettext('Deadline text'),
                text: this.deadlineRecord.formatTextOneline(50)
            }),
            items: []
        });
        this.callParent(arguments);
    }
});
