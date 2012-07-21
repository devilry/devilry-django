/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('devilry_subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudentsoverview',
    cls: 'managestudentsoverview sidebarlayout',
    requires: [
        'devilry_subjectadmin.view.managestudents.ListOfGroups'
    ],


    /**
     * @cfg {String} assignment_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            frame: false,
            dockedItems: [{
                xtype: 'toolbar',
                itemId: 'primaryToolbar',
                dock: 'top',
                //padding: '2 40 2 40',
                defaults: {
                    scale: 'medium',
                },
                items: [{
                    xtype: 'button',
                    itemId: 'selectButton',
                    text: gettext('Select'),
                    menu: [{
                        itemId: 'selectall',
                        text: gettext('Select all')
                    }, {
                        itemId: 'deselectall',
                        text: gettext('Deselect all')
                    }, '-', {
                        text: pgettext('group', 'Status'),
                        menu: [{
                            text: pgettext('group', 'Open')
                        }, {
                            text: pgettext('group', 'Closed')
                        }]
                    }, {
                        text: pgettext('group', 'Grade'),
                        menu: [{
                            text: pgettext('group', 'Failed')
                        }, {
                            text: pgettext('group', 'Passed')
                        }, '-', {
                            text: 'TODO: Will list of all current grades here unless there are more than XXX (20?)'
                        }]
                    }, {
                        text: gettext('Number of deliveries'),
                        menu: [{
                            text: gettext('No deliveries')
                        }, {
                            text: gettext('Has deliveries')
                        }, '-', {
                            text: 'TOOD: Will list all numbers of deliveries.'
                        }]
                    }, {
                        text: gettext('With examiner'),
                        menu: [{
                            text: 'TODO: Will list all related examiners'
                        }]
                    }, '-', {
                        text: gettext('Select using search ...')
                    }]
                }, {
                    xtype: 'combobox',
                    itemId: 'sortby',
                    queryMode: 'local',
                    valueField: 'value',
                    displayField: 'label',
                    forceSelection: true,
                    editable: false,
                    value: 'fullname', // NOTE: This must match the argument to _sortBy in _onRenderListOfGroups in the controller
                    store: Ext.create('Ext.data.Store', {
                        fields: ['value', 'label'],
                        data : [
                            {value:'fullname', label:"Sort by: Full name"},
                            {value:'lastname', label:"Sort by: Last name"},
                            {value:'username', label:"Sort by: Username"}
                        ]
                    })
                }, {
                    xtype: 'combobox',
                    itemId: 'viewselect',
                    queryMode: 'local',
                    valueField: 'value',
                    displayField: 'label',
                    forceSelection: true,
                    editable: false,
                    value: 'flat',
                    store: Ext.create('Ext.data.Store', {
                        fields: ['value', 'label'],
                        data : [
                            {value:'flat', label:"View: Flat"},
                            {value:'examiner', label:"View: Group by examiner"},
                            {value:'is_passing_grade', label:"View: Group by passed/failed"},
                            {value:'is_open', label:"View: Group by open/closed"},
                        ]
                    })
                }, '->', {
                    xtype: 'button',
                    text: 'Options',
                    menu: [{
                        text: gettext('Administrators are examiners on all'),
                        checked: false
                    }]
                }, {
                    xtype: 'textfield',
                    itemId: 'search',
                    //margin: '0 0 0 10',
                    width: 200,
                    emptyText: gettext('Search for students ...')
                }]
            }],

            items: [{
                xtype: 'listofgroups',
                //margin: '10 0 10 40',
                region: 'west',
                //border: false,
                resizable: true,
                width: 300
            }, {
                xtype: 'panel',
                region: 'center',
                //margin: '10 40 10 20',
                padding: '0 0 0 20',
                border: false,
                layout: 'fit',
                itemId: 'body'
            }],

            bbar: [{
                xtype: 'autocompletegroupwidget',
                flex: 1,
                hideTrigger: true,
                itemId: 'selectUsersByAutocompleteWidget'
            }]
        });
        this.callParent(arguments);
    }
});
