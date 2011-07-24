/** SearchWidget used in every page in the entire administrator interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.administrator.AdministratorSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],

    config: {
        /**
         * @cfg
         * Url prefix. Should be the absolute URL path to /administrator/.
         */
        urlPrefix: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Node rows.
         */
        nodeRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Subject rows.
         */
        subjectRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Period rows.
         */
        periodRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Assignment rows.
         */
        assignmentRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for AssignmentGroup rows.
         */
        assignmentgroupRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Delivery rows.
         */
        deliveryRowTpl: ''
    },

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
                        clickLinkTpl: this.urlPrefix + 'node/view/{id}'
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
                        clickLinkTpl: this.urlPrefix + 'subject/view/{id}'
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
                        clickLinkTpl: this.urlPrefix + 'period/view/{id}'
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
                        clickLinkTpl: this.urlPrefix + 'assignment/view/{id}'
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
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
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
