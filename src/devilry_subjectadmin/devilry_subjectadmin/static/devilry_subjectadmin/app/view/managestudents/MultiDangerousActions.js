Ext.define('devilry_subjectadmin.view.managestudents.MultiDangerousActions', {
    extend: 'devilry_subjectadmin.view.DangerousActions',
    alias: 'widget.multigroupdangerous',
    cls: 'devilry_subjectadmin_dangerousactions devilry_subjectadmin_multigroupdangerous',
    requires: [
        'devilry_extjsextras.SingleActionBox'
    ],

    initComponent: function() {
        Ext.apply(this, {
            titleTpl: '<h3>{heading}</h3>',
            items: [{
                xtype: 'singleactionbox',
                itemId: 'multiDeleteButton',
                margin: 0,
                id: 'multi_group_delete_button',
                titleText: gettext('Delete'),
                bodyHtml: interpolate(gettext('Once you delete a %(group_term)s, there is no going back. Only superusers can delete a %(group_term)s with deliveries.'), {
                    group_term: gettext('group')
                }, true),
                buttonText: gettext('Delete') + ' ...',
                buttonUi: 'danger'
            }]
        });
        this.callParent(arguments);
    }
});
