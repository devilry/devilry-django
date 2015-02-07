/**
 * List of all Subjects that the user have permission to view.
 */
Ext.define('devilry_subjectadmin.view.subject.ListAll' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectlistall',
    cls: 'devilry_subjectlistall bootstrap',
    requires: [
        'devilry_extjsextras.AlertMessageList'
    ],
    bodyPadding: 40,
    autoScroll: true,
    store: 'Subjects',

    listTpl: [
        '<ul>',
            '<tpl for=".">',
                '<li class="devilry_subject devilry_subject_{short_name}">',
                    '<a href="#/subject/{id}/">{long_name}</a>',
                '</li>',
            '</tpl>',
        '<ul>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                title: gettext("All my courses"),
                layout: 'fit',
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'dataview',
                    itemId: 'subjectList',
                    cls: 'devilry_allSubjectsList',
                    tpl: this.listTpl,
                    itemSelector: 'li.devilry_subject',
                    store: this.store
                }]
            }
        });
        this.callParent(arguments);
    }
});
