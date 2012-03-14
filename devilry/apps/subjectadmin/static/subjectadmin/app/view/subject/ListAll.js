/**
 * List of all Subjects that the user have permission to view.
 */
Ext.define('subjectadmin.view.subject.ListAll' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectlistall',
    cls: 'subjectlistall',
    requires: [
    ],
    layout: 'fit',
    bodyPadding: 40,
    autoScroll: true,
    store: 'Subjects',

    listTpl: [
        '<ul>',
            '<tpl for=".">',
                '<li style="margin-bottom: 10px;" class="subject">',
                    '<li><a href="#/{short_name}/">{long_name}</a></li>',
                '</li>',
            '</tpl>',
        '<ul>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                ui: 'inset-header-strong-panel',
                title: Ext.String.capitalize(dtranslate('core.subject.plural')),
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
