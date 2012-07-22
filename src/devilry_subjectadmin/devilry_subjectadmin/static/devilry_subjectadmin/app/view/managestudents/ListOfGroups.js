/**
 * List of groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.listofgroups',
    cls: 'devilry_subjectadmin_listofgroups',
    store: 'Groups',
    hideHeaders: true,

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    },

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'top',
        //padding: '2 40 2 40',
        //defaults: {
            //scale: 'medium',
        //},
        items: [{
            xtype: 'combobox',
            itemId: 'sortby',
            queryMode: 'local',
            valueField: 'value',
            displayField: 'label',
            forceSelection: true,
            editable: false,
            value: 'fullname', // NOTE: This must match the argument to _sortBy in _onRenderListOfGroups in the controller
            flex: 1,
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
            flex: 1,
            matchFieldWidth: false,
            store: Ext.create('Ext.data.Store', {
                fields: ['value', 'label'],
                data : [
                    {value:'flat', label:"View: Flat"},
                    {value:'examiner', label:"View: Group by examiner"},
                    {value:'is_passing_grade', label:"View: Group by passed/failed"},
                    {value:'is_open', label:"View: Group by open/closed"},
                ]
            })
        }]
    }, {
        xtype: 'toolbar',
        ui: 'footer',
        dock: 'bottom',
        defaults: {
            scale: 'medium',
        },
        items: [{
            xtype: 'button',
            itemId: 'selectButton',
            text: gettext('Select'),
            menu: {
                xtype: 'menu',
                plain: true,
                itemId: 'replaceSelectionMenu',
                items: [
                    Ext.String.format('<b>{0}:</b>', gettext('Replace current selection')),
                {
                    itemId: 'selectall',
                    text: gettext('Select all')
                }, {
                    itemId: 'deselectall',
                    text: gettext('Deselect all')
                }, {
                    itemId: 'invertselection',
                    text: gettext('Invert selection')
                }, '-', {
                    text: pgettext('group', 'Status'),
                    menu: [{
                        itemId: 'selectStatusOpen',
                        text: pgettext('group', 'Open')
                    }, {
                        itemId: 'selectStatusClosed',
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
                }]
            }
        }, {
            xtype: 'button',
            itemId: 'addToSelectionButton',
            text: gettext('Add to selection'),
            menu: {
                xtype: 'menu',
                plain: true,
                itemId: 'addToSelectionMenu',
                items: [Ext.String.format('<b>{0}:</b>', gettext('Add to current selection')),
                {
                    text: pgettext('group', 'Status'),
                    menu: [{
                        itemId: 'selectStatusOpen',
                        text: pgettext('group', 'Open')
                    }, {
                        itemId: 'selectStatusClosed',
                        text: pgettext('group', 'Closed')
                    }]
                }]
            }
        }, '->', {
            xtype: 'button',
            itemId: 'addstudents',
            iconCls: 'icon-add-24',
            text: gettext('Add students')
        }]
    }]
});
