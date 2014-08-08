Ext.define('devilry_student.view.groupinfo.Overview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.groupinfo',
    cls: 'devilry_student_groupinfo',

    /**
     * @cfg {Object} [group_id]
     */

    /**
     * @cfg {Object} [delivery_id]
     * ID of a delivery that should be highlighted on load.
     */

    /**
     * @cfg {bool} [add_delivery]
     * Show add delivery wizard on load?
     */

    layout: 'border',
    style: 'background: none !important;',

    items: [{
        xtype: 'box',
        region: 'north',
        hidden: true,
        itemId: 'notStudentOnPeriodBox',
        cls: 'notStudentOnPeriodBox',
        tpl: [
            '<a href="{moreinfourl}" target="_blank">',
                gettext('You are not registered as a student on {subject}. Click this box for more information.'),
            '</a>'
        ]
    }, {
        xtype: 'container',
        region: 'west',
        autoScroll: true,
        width: 250,
        padding: 20,
        itemId: 'metadataContainer'
    }, {
        xtype: 'container',
        autoScroll: true,
        region: 'center',
        layout: 'anchor',
        itemId: 'centerContainer',
        items: [{
            xtype: 'box',
            height: 'auto',
            region: 'north',
            padding: '20 20 0 20',
            itemId: 'titleBox',
            cls: 'bootstrap',
            tpl: [
                '<tpl if="groupinfo">',
                    '<h1>{groupinfo.breadcrumbs.assignment.long_name}</h1>',
                    '<p><small>',
                        '{groupinfo.breadcrumbs.subject.short_name}.',
                        '{groupinfo.breadcrumbs.period.short_name}.',
                        '{groupinfo.breadcrumbs.assignment.short_name}',
                    '</small></p>',
                '<tpl else>',
                    gettext('Loading') + ' ...',
                '</tpl>'
            ]
        }, {
            xtype: 'panel',
            bodyStyle: 'background-color: transparent !important;',
            bodyPadding: 20,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            itemId: 'deadlinesContainer',
            cls: 'devilry_discussionview_container'
        }]
    }]
});
