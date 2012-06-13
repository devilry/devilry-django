/**
 * List of all Subjects that the user have permission to view.
 */
Ext.define('devilry_subjectadmin.view.subject.ListAll' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectlistall',
    cls: 'subjectlistall bootstrap',
    requires: [
        'devilry_extjsextras.AlertMessageList'
    ],
    bodyPadding: 40,
    autoScroll: true,
    store: 'Subjects',

    listTpl: [
        '<ul>',
            '<tpl for=".">',
                '<li class="subject">',
                    '<a href="#/{short_name}/">{long_name}</a>',
                '</li>',
            '</tpl>',
        '<ul>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                ui: 'inset-header-strong-panel',
                title: dtranslate('core.subject.plural'),
                layout: 'fit',
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'dataview',
                    itemId: 'subjectList',
                    tpl: this.listTpl,
                    itemSelector: 'li.subject',
                    store: this.store
                }]
            },
        });
        this.callParent(arguments);
    }
});
