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
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedNodeStoreSearch'),
                filterconfig: {
                    type: 'node'
                },
                resultitemConfig: {
                    tpl: this.nodeRowTpl,
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'editors/node/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Subjects',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedSubjectStoreSearch'),
                filterconfig: {
                    type: 'subject'
                },
                resultitemConfig: {
                    tpl: this.subjectRowTpl,
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'editors/subject/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Periods',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedPeriodStoreSearch'),
                filterconfig: {
                    type: 'period'
                },
                resultitemConfig: {
                    tpl: this.periodRowTpl,
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'editors/period/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignments',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedAssignmentStoreSearch'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'editors/assignment/{id}'
                    },
                    menuitems: [{
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignment groups',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedAssignmentGroupStoreSearch'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: 'Edit',
                        clickLinkTpl: 'assignmentgroup/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Delivery',
                store: Ext.data.StoreManager.lookup('devilry.apps.administrator.simplified.SimplifiedDeliveryStoreSearch'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl
                }
            }]
        });
        this.callParent(arguments);
    }
});
