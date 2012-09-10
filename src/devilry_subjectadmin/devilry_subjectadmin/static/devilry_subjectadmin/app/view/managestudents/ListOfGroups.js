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
        'devilry_subjectadmin.view.managestudents.DynamicLoadMenu',
        'devilry_extjsextras.PrimaryButton',
        'Ext.grid.feature.Grouping',
        'Ext.grid.column.Action'
    ],

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    },

    initComponent: function() {
        //this.groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            //groupHeaderTpl: [
                //'<tpl if="groupField == \'is_open\'">',
                    //'<tpl if="groupValue">',
                        //gettext('Open'),
                    //'<tpl else>',
                        //gettext('Closed'),
                    //'</tpl>',
                //'<tpl else>',
                    //'{groupField}: {groupValue}',
                //'</tpl>',
            //]
        //});
        Ext.apply(this, {
            //features: [this.groupingFeature],
            //groupHeaderTpl: '',
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
                    
                    //xtype: 'combobox',
                    //itemId: 'viewselect',
                    //queryMode: 'local',
                    //valueField: 'value',
                    //displayField: 'label',
                    //forceSelection: true,
                    //editable: false,
                    //value: 'flat',
                    //flex: 1,
                    //matchFieldWidth: false,
                    //store: Ext.create('Ext.data.Store', {
                        //fields: ['value', 'label'],
                        //data : [
                            //{value:'flat', label:"View: Flat"},
                            //{value:'examiner', label:"View: Group by examiner"},
                            //{value:'is_passing_grade', label:"View: Group by passed/failed"},
                            //{value:'is_open', label:"View: Group by open/closed"},
                        //]
                    //})
                }]
            }, {
                xtype: 'toolbar',
                ui: 'footer',
                dock: 'bottom',
                defaults: {
                    scale: 'large'
                },
                items: [{
                    xtype: 'button',
                    itemId: 'selectButton',
                    cls: 'selectButton',
                    text: gettext('Select'),
                    menu: this._createSelectMenu({
                        itemId: 'replaceSelectionMenu',
                        cls: 'replaceSelectionMenu',
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
                    cls: 'addToSelectionButton',
                    text: gettext('Add to selection'),
                    menu: this._createSelectMenu({
                        title: gettext('Add to current selection'),
                        itemId: 'addToSelectionMenu'
                    })
                }, '->', {
                    xtype: 'primarybutton',
                    itemId: 'addstudents',
                    cls: 'addstudents',
                    text: gettext('Add students')
                }]
            }]
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
            cls: 'byStatusButton',
            hideOnClick: false,
            menu: {
                xtype: 'menu',
                cls: 'byStatusMenu',
                items: [{
                    itemId: 'selectStatusOpen',
                    cls: 'selectStatusOpen',
                    text: pgettext('group', 'Open')
                }, {
                    itemId: 'selectStatusClosed',
                    cls: 'selectStatusClosed',
                    text: pgettext('group', 'Closed')
                }]
            }

        // Feedback
        }, {
            text: pgettext('group', 'By feedback'),
            cls: 'byFeedbackButton',
            hideOnClick: false,
            menu: {
                xtype: 'menu',
                cls: 'byFeedbackMenu',
                items: [{
                    itemId: 'selectGradePassed',
                    cls: 'selectGradePassed',
                    text: pgettext('group', 'Passed')
                }, {
                    itemId: 'selectGradeFailed',
                    cls: 'selectGradeFailed',
                    text: pgettext('group', 'Failed')
                }, '-', {
                    itemId: 'selectHasFeedback',
                    cls: 'selectHasFeedback',
                    text: pgettext('group', 'Has feedback')
                }, {
                    itemId: 'selectNoFeedback',
                    cls: 'selectNoFeedback',
                    text: pgettext('group', 'No feedback')
                }, '-', {
                    text: pgettext('group', 'Grade'),
                    cls: 'selectByFeedbackWithGrade',
                    hideOnClick: false,
                    menu: {
                        xtype: 'dynamicloadmenu',
                        itemId: 'specificGradeMenu'
                    }
                }, {
                    text: pgettext('points', 'Points'),
                    cls: 'selectByFeedbackWithPoints',
                    hideOnClick: false,
                    menu: {
                        xtype: 'dynamicloadmenu',
                        itemId: 'specificPointsMenu'
                    }
                }]
            }

        // Number of deliveries
        }, {
            text: gettext('By number of deliveries'),
            cls: 'byDeliveryNumButton',
            hideOnClick: false,
            menu: {
                xtype: 'menu',
                cls: 'byDeliveryMenu',
                items: [{
                    itemId: 'selectHasDeliveries',
                    cls: 'selectHasDeliveries',
                    text: gettext('Has deliveries')
                }, {
                    itemId: 'selectNoDeliveries',
                    cls: 'selectNoDeliveries',
                    text: gettext('No deliveries')
                }, {
                    text: pgettext('numdeliveries', 'Exact number'),
                    cls: 'selectByDeliveryExactNum',
                    hideOnClick: false,
                    menu: {
                        xtype: 'dynamicloadmenu',
                        itemId: 'specificNumDeliveriesMenu'
                    }
                }]
            }

        // By examiner
        }, {
            text: gettext('By examiner'),
            cls: 'byExaminerButton',
            hideOnClick: false,
            menu: {
                xtype: 'menu',
                cls: 'byExaminerMenu',
                items: [{
                    itemId: 'selectHasExaminer',
                    cls: 'selectHasExaminer',
                    text: gettext('Has examiner(s)')
                }, {
                    itemId: 'selectNoExaminer',
                    cls: 'selectNoExaminer',
                    text: gettext('No examiner(s)')
                }, {
                    text: gettext('Specific examiner'),
                    cls: 'selectBySpecificExaminer',
                    hideOnClick: false,
                    menu: {
                        xtype: 'dynamicloadmenu',
                        itemId: 'specificExaminerMenu'
                    }
                }]
            }

        // By tag
        }, {
            text: gettext('By tag'),
            cls: 'byTagButton',
            hideOnClick: false,
            menu: {
                xtype: 'menu',
                cls: 'byTagMenu',
                items: [{
                    itemId: 'selectHasTag',
                    cls: 'selectHasTag',
                    text: gettext('Has tag(s)')
                }, {
                    itemId: 'selectNoTag',
                    cls: 'selectNoTag',
                    text: gettext('No tag(s)')
                }, {
                    text: gettext('Specific tag'),
                    cls: 'selectBySpecificTac',
                    hideOnClick: false,
                    menu: {
                        xtype: 'dynamicloadmenu',
                        itemId: 'specificTagMenu'
                    }
                }]
            }
        }]);
        var menu = {
            xtype: 'menu',
            plain: true,
            itemId: config.itemId,
            cls: config.cls,
            items: menuitems
        }
        return menu;
    }
});
