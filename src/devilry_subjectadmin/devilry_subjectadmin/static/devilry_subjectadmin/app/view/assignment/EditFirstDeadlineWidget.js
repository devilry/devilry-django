Ext.define('devilry_subjectadmin.view.assignment.EditFirstDeadlineWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editfirstdeadline-widget',
    cls: 'devilry_subjectadmin_editfirstdeadline_widget',

    requires: [
        'devilry_subjectadmin.view.assignment.EditFirstDeadlinePanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'editablesidebarbox',
                itemId: 'readFirstDeadline',
                disabled: true,
                title: gettext('First deadline'),
                bodyTpl: [
                    '<tpl if="text">',
                        '<p class="muted">{text}</small>',
                    '<tpl else>',
                        '<tpl if="first_deadline">',
                            '<p class="muted">{first_deadline}</p>',
                        '<tpl else>',
                            '<p>',
                                '<span class="text-warning">',
                                    gettext('This assignment has no first deadline set.'),
                                '<span>',
                                ' ',
                                '<small class="text-warning">',
                                     gettext('The cause of this warning may that an administrator on this assignment has decided that they want to manually set the first deadline on all new groups, or some third-party integration with a bug, or that the assignment was created with Devilry version 1.1 or older. You should set a first deadline if you plan on adding any more groups to this assignment.'),
                                '</small>',
                            '</p>',
                        '</tpl>',
                        '<p><small class="muted">',
                            gettext('The first deadline is the deadline added to groups when they are added to the assignment. Editing it does not affect existing groups.'),
                        '</small></p>',
                    '</tpl>',
                ]
            }, {
                xtype: 'editfirstdeadlinepanel',
                itemId: 'editFirstDeadline'
            }]
        });
        this.callParent(arguments);
    }
});
