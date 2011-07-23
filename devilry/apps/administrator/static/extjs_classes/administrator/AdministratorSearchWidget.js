Ext.define('devilry.administrator.AdministratorSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: 'Nodes',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedNodeStore'),
                filterconfig: {
                    type: 'node'
                },
                resultitemConfig: {
                    tpl: '{id}',
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'node/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Subjects',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedSubjectStore'),
                filterconfig: {
                    type: 'subject'
                },
                resultitemConfig: {
                    tpl: '{id}',
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'subject/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Periods',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedPeriodStore'),
                filterconfig: {
                    type: 'period'
                },
                resultitemConfig: {
                    tpl: '{id}',
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'period/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignments',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedAssignmentStore'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: '{id}',
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'assignment/{id}'
                    },
                    menuitems: [{
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignment groups',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedAssignmentGroupStore'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: '{id}',
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'assignmentgroup/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Delivery',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedDeliveryStore'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: '{id}'
                }
            }]
        });
        this.callParent(arguments);
    }
});
