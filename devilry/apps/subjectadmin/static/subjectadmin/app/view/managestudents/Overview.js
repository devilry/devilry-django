/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudentsoverview',
    cls: 'managestudentsoverview sidebarlayout',
    requires: [
        'subjectadmin.view.managestudents.ListOfGroups'
    ],


    /**
     * @cfg {String} subject_shortname (required)
     */

    /**
     * @cfg {String} period_shortname (required)
     */

    /**
     * @cfg {String} assignment_shortname (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            frame: false,
            dockedItems: [{
                xtype: 'toolbar',
                itemId: 'primaryToolbar',
                dock: 'top',
                padding: {top: 2, right: 40, bottom: 2, left: 40},
                defaults: {
                    scale: 'medium',
                },
                items: [{
                    xtype: 'combobox',
                    itemId: 'sortby',
                    queryMode: 'local',
                    valueField: 'value',
                    displayField: 'label',
                    forceSelection: true,
                    editable: false,
                    value: 'fullname',
                    store: Ext.create('Ext.data.Store', {
                        fields: ['value', 'label'],
                        data : [
                            {value:'lastname', label:"Sort by: Last name"},
                            {value:'username', label:"Sort by: Username"},
                            {value:'fullname', label:"Sort by: Full name"}
                        ]
                    })
                }, {
                    xtype: 'button',
                    itemId: 'selectall',
                    text: dtranslate('themebase.selectall')
                }, '->', {
                    xtype: 'button',
                    text: 'Options',
                    menu: [{
                        text: dtranslate('subjectadmin.managestudents.make_admins_examiner'),
                        checked: false
                    }]
                }, {
                    xtype: 'textfield',
                    itemId: 'search',
                    margin: {left: 10},
                    width: 200,
                    emptyText: dtranslate('subjectadmin.managestudents.search_emptytext')
                }]
            }],
            items: [{
                xtype: 'listofgroups',
                margin: {top:10, right: 0, bottom: 10, left: 20},
                region: 'west',
                //border: false,
                resizable: true,
                width: 300
            }, {
                xtype: 'panel',
                region: 'center',
                margin: {top:10, right: 20, bottom: 10, left: 20},
                border: false,
                itemId: 'body'
            }]
        });
        this.callParent(arguments);
    }
});
