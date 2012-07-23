/**
 * List of groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'devilry_subjectadmin.view.managestudents.GridOfGroupsBase',
    alias: 'widget.listofgroups',
    cls: 'devilry_subjectadmin_listofgroups',
    store: 'Groups',
    hideHeaders: true,

    requires: [
        'devilry_subjectadmin.view.managestudents.DynamicLoadMenu'
    ],

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    },

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
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
                    menu: this._createSelectMenu({
                        itemId: 'replaceSelectionMenu',
                        title: gettext('Replace current selection'),
                        prefixItems: [{
                            itemId: 'selectall',
                            text: gettext('Select all') + ' <small>(CTRL-a)</small>'
                        }, {
                            itemId: 'deselectall',
                            text: gettext('Deselect all')
                        }, {
                            itemId: 'invertselection',
                            text: gettext('Invert selection')
                        }, '-']
                    })
                }, {
                    xtype: 'button',
                    itemId: 'addToSelectionButton',
                    text: gettext('Add to selection'),
                    menu: this._createSelectMenu({
                        title: gettext('Add to current selection'),
                        itemId: 'addToSelectionMenu'
                    })
                }, '->', {
                    xtype: 'button',
                    itemId: 'addstudents',
                    iconCls: 'icon-add-24',
                    text: gettext('Add students')
                }]
            }],
        });
        this.callParent(arguments);
    },


    /**
     * @param {String} [config.title] Title of the menu
     * @param {[Object]} [config.prefixItems] Prefixed to the items in the menu, under the title.
     */
    _createSelectMenu: function(config) {
        var menuitems = [Ext.String.format('<b>{0}:</b>', config.title)];
        if(config.prefixItems) {
            Ext.Array.push(menuitems, config.prefixItems);
        }
        Ext.Array.push(menuitems, [{

        // Status
            text: pgettext('group', 'By status'),
            menu: [{
                itemId: 'selectStatusOpen',
                text: pgettext('group', 'Open')
            }, {
                itemId: 'selectStatusClosed',
                text: pgettext('group', 'Closed')
            }]

        // Feedback
        }, {
            text: pgettext('group', 'By feedback'),
            menu: [{
                itemId: 'selectGradePassed',
                text: pgettext('group', 'Passed')
            }, {
                itemId: 'selectGradeFailed',
                text: pgettext('group', 'Failed')
            }, {
                text: pgettext('group', 'Grade'),
                menu: {
                    xtype: 'dynamicloadmenu',
                    itemId: 'specificGradeMenu'
                }
            }, {
                text: pgettext('points', 'Points'),
                menu: {
                    xtype: 'dynamicloadmenu',
                    itemId: 'specificPointsMenu'
                }
            }]

        // Number of deliveries
        }, {
            text: gettext('By number of deliveries'),
            menu: [{
                itemId: 'selectHasDeliveries',
                text: gettext('Has deliveries')
            }, {
                itemId: 'selectNoDeliveries',
                text: gettext('No deliveries')
            }, {
                text: pgettext('numdeliveries', 'Exact number'),
                menu: {
                    xtype: 'dynamicloadmenu',
                    itemId: 'specificNumDeliveriesMenu'
                }
            }]

        // By examiner
        }, {
            text: gettext('By examiner'),
            menu: [{
                itemId: 'selectHasExaminer',
                text: gettext('Has examiner(s)')
            }, {
                itemId: 'selectNoExaminer',
                text: gettext('No examiner(s)')
            }, {
                text: gettext('Specific examiner'),
                menu: {
                    xtype: 'dynamicloadmenu',
                    itemId: 'specificExaminerMenu'
                }
            }]

        // By tag
        }, {
            text: gettext('By tag'),
            menu: [{
                itemId: 'selectHasTag',
                text: gettext('Has tag(s)')
            }, {
                itemId: 'selectNoTag',
                text: gettext('No tag(s)')
            }, {
                text: gettext('Specific tag'),
                menu: {
                    xtype: 'dynamicloadmenu',
                    itemId: 'specificTagMenu'
                }
            }]
        }]);
        var menu = {
            xtype: 'menu',
            plain: true,
            itemId: config.itemId,
            items: menuitems
        }
        return menu;
    }
});
