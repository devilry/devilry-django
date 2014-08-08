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
        'devilry_subjectadmin.view.managestudents.SelectGroupsBySearchWidget',
        'devilry_subjectadmin.view.managestudents.SelectedGroupsButton',
        'devilry_subjectadmin.view.managestudents.SortByButton',
        'devilry_extjsextras.GridBigButtonCheckboxModel',
        'devilry_extjsextras.PrimaryButton',
        'Ext.grid.feature.Grouping',
        'Ext.grid.column.Action',
        'Ext.selection.CheckboxModel'
    ],

    getColumns: function() {
        return [this.getGroupInfoColConfig(), this.getMetadataColConfig()];
    },

    initComponent: function() {
        Ext.apply(this, {
            //selModel: Ext.create('Ext.selection.CheckboxModel'),
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [{
                    xtype: 'selectgroupsbysearch',
                    grid: this,
                    flex: 1
                }]
            }, {
                xtype: 'toolbar',
                dock: 'top',
                items: [{
                    xtype: 'button',
                    text: gettext('Select'),
                    cls: 'selectButton',
                    menu: {
                        xtype: 'menu',
                        cls: 'selectMenu',
                        items: [{
                            itemId: 'selectall',
                            cls: 'selectAllButton',
                            text: gettext('Select all') + ' <small>(CTRL-a)</small>'
                        }, {
                            itemId: 'deselectall',
                            cls: 'deselectAllButton',
                            text: gettext('Deselect all')
                        }, {
                            itemId: 'invertselection',
                            cls: 'invertSelectionButton',
                            text: gettext('Invert selection')
                        }, '-', {
                            text: gettext('Replace current selection'),
                            cls: 'replaceSelectionButton',
                            itemId: 'replaceSelectionButton',
                            hideOnClick: false,
                            menu: this._createSelectMenu({
                                itemId: 'replaceSelectionMenu',
                                cls: 'replaceSelectionMenu',
                                title: gettext('Replace current selection')
                            })
                        }, {
                            itemId: 'addToSelectionButton',
                            cls: 'addToSelectionButton',
                            text: gettext('Add to current selection'),
                            hideOnClick: false,
                            menu: this._createSelectMenu({
                                title: gettext('Add to current selection'),
                                itemId: 'addToSelectionMenu',
                                cls: 'addToSelectionMenu'
                            })
                        }, {
                            itemId: 'removeFromSelectionButton',
                            cls: 'removeFromSelectionButton',
                            text: gettext('Remove from current selection'),
                            hideOnClick: false,
                            menu: this._createSelectMenu({
                                title: gettext('Remove from current selection'),
                                itemId: 'removeFromSelectionMenu',
                                cls: 'removeFromSelectionMenu'
                            })
                        }]
                    }
                }, {
                    xtype: 'sortgroupsbybutton',
                    grid: this
                }, '->', {
                    xtype: 'selectedgroupsbutton',
                    grid: this
                }]
            }, {
                xtype: 'toolbar',
                //ui: 'footer',
                dock: 'bottom',
                defaults: {
                    scale: 'large'
                },
                items: ['->', {
                    xtype: 'button',
                    scale: 'medium',
                    itemId: 'addstudents',
                    cls: 'addstudents',
                    text: [
                        '<i class="icon-plus"></i> ',
                        gettext('Add students')
                    ].join('')
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
        };
        return menu;
    }
});
